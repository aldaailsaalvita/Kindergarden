from django.contrib import admin
from .models import AbstractUser, Murid, TransaksiPembayaran, ForumDiskusi, Komentar, Berita, MataPelajaran, Nilai

# ModelAdmin untuk AbstractUser
class AbstractUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'roles', 'status', 'created', 'updated')
    list_filter = ('status', 'roles')
    search_fields = ('name', 'roles')
    ordering = ('-created',)

# ModelAdmin untuk Murid
class MuridAdmin(admin.ModelAdmin):
    list_display = ('name', 'jenis_kelamin', 'status', 'kelas', 'ortu', 'created', 'updated')
    list_filter = ('status', 'kelas', 'ortu')
    search_fields = ('name', 'ortu__name')  # Mencari berdasarkan nama orang tua (AbstractUser)
    ordering = ('-created',)

# ModelAdmin untuk Transaksi Pembayaran
class TransaksiPembayaranAdmin(admin.ModelAdmin):
    list_display = ('transaksi_id', 'murid', 'keterangan', 'jumlah', 'status', 'created', 'updated')
    list_filter = ('status', 'murid')
    search_fields = ('transaksi_id', 'murid__name')
    ordering = ('-created',)

# ModelAdmin untuk Forum Diskusi
class ForumDiskusiAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created', 'updated')
    list_filter = ('status', 'author')
    search_fields = ('title', 'author__name')
    ordering = ('-created',)

# ModelAdmin untuk Komentar
class KomentarAdmin(admin.ModelAdmin):
    list_display = ('komentar_id', 'author', 'komentar', 'created', 'updated')
    list_filter = ('author',)
    search_fields = ('komentar', 'author__name')
    ordering = ('-created',)

# ModelAdmin untuk Berita
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'jenis', 'created', 'updated')
    list_filter = ('jenis', 'author')
    search_fields = ('title', 'author__name', 'content')
    ordering = ('-created',)

# ModelAdmin untuk Mata Pelajaran
class MataPelajaranAdmin(admin.ModelAdmin):
    list_display = ('nama', 'created', 'updated')
    search_fields = ('nama',)
    ordering = ('-created',)

# ModelAdmin untuk Nilai
class NilaiAdmin(admin.ModelAdmin):
    list_display = ('guru', 'murid', 'mapel', 'nilai', 'created', 'updated')
    list_filter = ('guru', 'murid', 'mapel')
    search_fields = ('guru__name', 'murid__name', 'mapel__nama')
    ordering = ('-created',)

# Mendaftarkan model ke admin
admin.site.register(AbstractUser, AbstractUserAdmin)
admin.site.register(Murid, MuridAdmin)
admin.site.register(TransaksiPembayaran, TransaksiPembayaranAdmin)
admin.site.register(ForumDiskusi, ForumDiskusiAdmin)
admin.site.register(Komentar, KomentarAdmin)
admin.site.register(Berita, BeritaAdmin)
admin.site.register(MataPelajaran, MataPelajaranAdmin)
admin.site.register(Nilai, NilaiAdmin)
