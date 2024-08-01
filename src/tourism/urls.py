"""
URL configuration for tourism project.

"""
from django.conf import settings
from django.conf.urls.static import static 
from django.contrib import admin
from django.urls import path, re_path, include
from .settings import SITE_NAME
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from profiles.views import ExchangeRatesView

fcm_router = DefaultRouter()

fcm_router.register("devices", FCMDeviceAuthorizedViewSet, "fcm-devices")

admin.site.site_header = f'{SITE_NAME} administration'
admin.site.site_title = f'{SITE_NAME} site admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('app_auth.urls')),
    path('profiles/', include('profiles.urls')),
    path('services/activities/', include('activities.urls')),
    path('reservations/', include('reservations.urls')),
    path('services/', include('services.urls')),
    path('tags/', include('tags.urls')),
    path('events/', include('events.urls')),
    path('services/properties/',include('properties.urls')),
    path('fcm/', include(fcm_router.urls)),
    path('inbox/', include('inbox.urls')),
    path('exchange_rates/', ExchangeRatesView.as_view())
]  + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]
urlpatterns += staticfiles_urlpatterns()

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]