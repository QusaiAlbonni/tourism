from django.urls import path
from django.urls import path, re_path, include
from app_auth.views import WebLoginView, UserActivationView


urlpatterns = [
    re_path(r'', include('djoser.urls')),
    re_path(r'', include('djoser.urls.jwt')),
    path('login/web/', WebLoginView.as_view(), name='web-login'),
    path('activation/<str:uid>/<str:token>/', UserActivationView.as_view()),
]