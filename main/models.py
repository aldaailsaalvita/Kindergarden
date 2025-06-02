import uuid
from django.db import models
from django.contrib.auth.models import User

from web.helper import RandomFileName


class AbstractUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(null=False, blank=False, max_length=255)
    roles = models.CharField(null=False, blank=False, max_length=255)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Murid(models.Model):
    murid_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    jenis_kelamin = models.CharField(max_length=255)
    foto = models.ImageField(upload_to=RandomFileName('murid/foto/'), null=True, blank=True)
    tanggal_lahir = models.DateField(null=False, blank=False)
    status = models.BooleanField()
    ortu = models.ForeignKey(AbstractUser, on_delete=models.DO_NOTHING)
    kelas = models.BigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'Murid'

    def __str__(self):
        return self.name
    
class TransaksiPembayaran(models.Model):
    transaksi_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bukti_pembayaran = models.ImageField(upload_to=RandomFileName('transaksi/bukti/'), null=True, blank=True)
    status = models.BooleanField()
    murid = models.ForeignKey(Murid, on_delete=models.DO_NOTHING)
    jumlah = models.BigIntegerField(default=0)
    keterangan = models.CharField(null=True, blank=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'TransaksiPembayaran'

    def __str__(self):
        return self.murid.name

class ForumDiskusi(models.Model):
    forum_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    foto = models.ImageField(upload_to=RandomFileName('forum/foto/'), null=True, blank=True)
    title = models.CharField(null=True, blank=True, max_length=255)
    status = models.BooleanField()
    author = models.ForeignKey(AbstractUser, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'ForumDiskusi'

    def __str__(self):
        return self.author.name

class Komentar(models.Model):
    komentar_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(AbstractUser, on_delete=models.DO_NOTHING)
    foto = models.ImageField(upload_to=RandomFileName('forum/komentar/'), null=True, blank=True)
    komentar = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'Komentar'

    def __str__(self):
        return self.author.name

class Berita(models.Model):
    berita_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(AbstractUser, on_delete=models.DO_NOTHING)
    foto = models.ImageField(upload_to=RandomFileName('berita/foto/'), null=True, blank=True)
    jenis = models.CharField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    content = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'Berita'

    def __str__(self):
        return self.author.name

class MataPelajaran(models.Model):
    mapel_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(null=False, blank=False, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'MataPelajaran'

    def __str__(self):
        return self.nama

class Nilai(models.Model):
    nilai_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guru = models.ForeignKey(AbstractUser, on_delete=models.DO_NOTHING)
    murid = models.ForeignKey(Murid, on_delete=models.DO_NOTHING)
    mapel = models.ForeignKey(MataPelajaran, on_delete=models.DO_NOTHING)
    nilai = models.BigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  
        db_table = 'Nilai'

    def __str__(self):
        return f"{self.murid.name} - Nilai : {self.nilai}"

