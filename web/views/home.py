from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.db.models import Avg

from main.models import AbstractUser, MataPelajaran, Murid, Nilai, TransaksiPembayaran
from main.serializers import MuridSerializer, NilaiSerializer

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                abstract_user = AbstractUser.objects.get(user=user)
                
                if abstract_user.status:  
                    auth_login(request, user)
                    request.session['user_id'] = abstract_user.id
                    request.session['name'] = abstract_user.name.upper()
                    print(abstract_user.roles)
                    if int( abstract_user.roles) == 1:
                        request.session['roles'] = "GURU"
                    elif int(abstract_user.roles) == 2:
                        request.session['roles'] = "ORTU"
                    else:
                        request.session['roles'] = "ADMIN"
                    messages.success(request, 'Login Berhasil')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Akun Anda belum disetujui oleh admin, silakan tunggu persetujuan.')
                    return redirect('login')
            except AbstractUser.DoesNotExist:
                messages.error(request, 'Pengguna tidak ditemukan dalam sistem.')
                return redirect('login')
        else:
            messages.error(request, 'Username atau password salah')  
            return redirect('login')
    
    return render(request, 'templates/auth/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        name = request.POST.get('name')
        role = request.POST.get('roles') 

        # Validasi password
        if password != confirm_password:
            messages.error(request, 'Password dan konfirmasi password tidak cocok.')
            return redirect('signup')

        # Validasi username dan email (optional: bisa ditambahkan pengecekan lebih lanjut)
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah terdaftar.')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return redirect('signup')

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=name  
            )

            # Menambahkan data pada model AbstractUser
            abstract = AbstractUser()
            abstract.user = user
            abstract.name = name
            abstract.roles = role
            if role == 2:
                abstract.status = True
            abstract.save()

            # Autentikasi dan login setelah registrasi
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  
                messages.success(request, 'Akun berhasil dibuat dan menunggu di approve oleh admin.')
                return redirect('login') 
            else:
                messages.error(request, 'Terjadi kesalahan saat login setelah registrasi.')
                return redirect('signup')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('signup')
    
    return render(request, 'templates/auth/signup.html')

def oidc_logout(request):
    logout(request)  
    return redirect('login') 

def index(request):
    return render(request, 'templates/homepage/index.html')

def dashboard(request):
    return render(request, 'templates/dashboard/index.html')

def anak(request):
    murid = Murid.objects.all()
    if request.session.get('roles') == "ORTU":
        murid = Murid.objects.filter(ortu=request.session.get('user_id'))
    
    if request.GET.get('search'):
        murid = murid.filter(name__icontains=request.GET.get('search'))

    if request.method == 'POST':
        name = request.POST.get('name')
        jenis_kelamin = request.POST.get('jenis_kelamin')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        kelas = request.POST.get('kelas')
        foto = request.FILES.get('foto')  
        status = request.POST.get('status') == 'on'  
        ortu_id = request.session.get('user_id')  
        ortu = AbstractUser.objects.get(id=ortu_id)
        try:
            Murid.objects.create(
                name=name,
                jenis_kelamin=jenis_kelamin,
                tanggal_lahir=tanggal_lahir,
                kelas=kelas,
                foto=foto,
                status=status,
                ortu=ortu
            )
            messages.success(request, 'Murid berhasil ditambahkan.')
            redirect('anak')
        except ortu.DoesNotExist:
            messages.error(request, 'Data orang tua tidak ditemukan.')
            redirect('anak')
        except Exception as e:
            messages.error(request, f'Kesalahan: {str(e)}')
            redirect('anak')
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    srz = MuridSerializer(murid, many=True)

    paginator = Paginator(srz.data, limit)

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'data' : items
    }
    return render(request, 'templates/anak/index.html', context=context)

def nilai_akademik(request):
    nilai = Nilai.objects.all().order_by('-updated')
    if request.session.get('roles') == "ORTU":
        nilai = Nilai.objects.filter(murid__ortu=request.session.get('user_id'))
    
    if request.GET.get('search'):
        nilai = nilai.filter(murid__name__icontains=request.GET.get('search'))
    
    if request.method == 'POST':
        murid_id = request.POST.get('murid_id')
        mapel_id = request.POST.get('mapel_id')
        nilai = request.POST.get('nilai')

        nil = Nilai.objects.filter(murid=murid_id, mapel=mapel_id, updated__year=datetime.now().year)
        if nil:
            messages.error(request, 'Data Murid Sudah ada di mapel yang sama.')
            return redirect('nilai_akademik')  # Ganti dengan nam            
        try:
            murid = Murid.objects.get(pk=murid_id)
            mapel = MataPelajaran.objects.get(pk=mapel_id)

            # Simpan data Nilai
            Nilai.objects.create(
                guru_id=request.session.get('user_id'),
                murid=murid,
                mapel=mapel,
                nilai=int(nilai)
            )

            messages.success(request, 'Data nilai berhasil ditambahkan.')
            return redirect('nilai_akademik')  # Ganti dengan nama URL tujuan
        except Murid.DoesNotExist:
            messages.error(request, 'Murid tidak ditemukan.')
            return redirect('nilai_akademik')  # Ganti dengan nama URL tujuan
        except MataPelajaran.DoesNotExist:
            messages.error(request, 'Mata pelajaran tidak ditemukan.')
            return redirect('nilai_akademik')  # Ganti dengan nama URL tujuan
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {e}')
            return redirect('nilai_akademik')  # Ganti dengan nama URL tujuan

    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    srz = NilaiSerializer(nilai, many=True)

    paginator = Paginator(srz.data, limit)

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'data' : items,
        'murid_list': Murid.objects.all(),
        'mapel_list': MataPelajaran.objects.all(),

    }
    return render(request, 'templates/nilai_akademik/index.html', context=context)

def pembayaran(request):
    transaksi = TransaksiPembayaran.objects.all().order_by('-updated')

    # Filter jika role adalah "ORTU"
    if request.session.get('roles') == "ORTU":
        transaksi = transaksi.filter(murid__ortu=request.session.get('user_id'))

    # Fitur pencarian berdasarkan nama murid
    if request.GET.get('search'):
        transaksi = transaksi.filter(murid__name__icontains=request.GET.get('search'))

    # Handle POST untuk tambah transaksi pembayaran
    if request.method == 'POST':
        murid_id = request.POST.get('murid_id')
        jumlah = request.POST.get('jumlah')
        keterangan = request.POST.get('keterangan')
        bukti_pembayaran = request.FILES.get('bukti_pembayaran')  # Ambil file gambar

        try:
            # Ambil data murid
            murid = Murid.objects.get(pk=murid_id)

            # Simpan data transaksi pembayaran
            TransaksiPembayaran.objects.create(
                murid=murid,
                jumlah=int(jumlah),
                keterangan=keterangan,
                bukti_pembayaran=bukti_pembayaran,
                status=False  # Default status pembayaran adalah False (belum dikonfirmasi)
            )

            messages.success(request, 'Transaksi pembayaran berhasil ditambahkan.')
            return redirect('pembayaran')  # Ganti dengan nama URL tujuan
        except Murid.DoesNotExist:
            messages.error(request, 'Murid tidak ditemukan.')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {e}')

    # Paginasi
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    paginator = Paginator(transaksi, limit)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    # Context untuk template
    context = {
        'data': items,
        'murid_list': Murid.objects.all(),
    }
    return render(request, 'templates/pembayaran/index.html', context=context)

def prestasi_chart_data(request):
    # Hitung rata-rata nilai per mapel
    rata_rata_mapel = (
            Nilai.objects
            .values('mapel__nama')  # Nama mata pelajaran
            .annotate(average=Avg('nilai'))
            .order_by('mapel__nama')
        )
    if request.session.get('roles') == "ORTU":
        rata_rata_mapel = (
            Nilai.objects.filter(murid__ortu=request.session.get('user_id'))
            .values('mapel__nama')  # Nama mata pelajaran
            .annotate(average=Avg('nilai'))
            .order_by('mapel__nama')
        )

    # Struktur data JSON
    labels = [item['mapel__nama'] for item in rata_rata_mapel]
    averages = [item['average'] for item in rata_rata_mapel]

    data = {
        "labels": labels,
        "averages": averages
    }

    return JsonResponse(data)

def prestasi_siswa_chart_data(request):
    # Hitung rata-rata nilai per siswa
    rata_rata_siswa = (
        Nilai.objects
        .values('murid__name')  # Nama siswa
        .annotate(average=Avg('nilai'))
        .order_by('-average')
    )

    if request.session.get('roles') == "ORTU":
        rata_rata_siswa = (
            Nilai.objects.filter(murid__ortu=request.session.get('user_id'))
            .values('murid__name')  # Nama siswa
            .annotate(average=Avg('nilai'))
            .order_by('-average')
        )

    # Struktur data JSON
    names = [item['murid__name'] for item in rata_rata_siswa]
    averages = [item['average'] for item in rata_rata_siswa]

    data = {
        "names": names,
        "averages": averages
    }

    return JsonResponse(data)