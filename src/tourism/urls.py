"""
URL configuration for tourism project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from .settings import SITE_NAME

admin.site.site_header = f'{SITE_NAME} administration'
admin.site.site_title = f'{SITE_NAME} site admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('djoser.social.urls')),
    path('auth/', include('app_auth.urls')),
    path('profiles/', include('profiles.urls')),
    path('activities/', include('activities.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
