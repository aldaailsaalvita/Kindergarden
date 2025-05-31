from datetime import datetime
import json
from rest_framework import serializers
from decimal import Decimal
from main.models import Murid, Nilai
from django.db.models import Sum


class MuridSerializer(serializers.ModelSerializer):
    nilai_rata = serializers.SerializerMethodField()
    
    def get_nilai_rata(self, obj):
        list_nilai = Nilai.objects.filter(
            murid=obj.murid_id)
        nilai = 0
        
        if list_nilai:
            for x in list_nilai:
                nilai += x.nilai
            nilai = nilai/list_nilai.count()
        return nilai

    class Meta:
        model = Murid
        fields = '__all__'
        depth = 1

class NilaiSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nilai
        fields = '__all__'
        depth = 1