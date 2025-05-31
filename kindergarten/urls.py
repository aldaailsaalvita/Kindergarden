"""kindergarten URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from web.views import home

urlpatterns = (
    [
        path('admin/', admin.site.urls),
        path('', home.index, name='homepage'),
        path('dashboard/', home.dashboard, name='dashboard'),
        path('login/', home.login, name='login'),
        path('signup/', home.signup, name='signup'),
        path('logout/', home.oidc_logout, name='logout'),
        path('anak/', home.anak, name='anak'),
        path('nilai_akademik/', home.nilai_akademik, name='nilai_akademik'),
        path('pembayaran/', home.pembayaran, name='pembayaran'),
        path('prestasi/data/', home.prestasi_chart_data, name='prestasi_chart_data'),
        path('prestasi/chart-siswa-data/', home.prestasi_siswa_chart_data, name='chart_siswa_data'),

        
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
