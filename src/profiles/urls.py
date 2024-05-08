from django.urls import path
from django.urls import path, re_path, include
from .views import ProfileAddressView, ProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", ProfileViewSet)

urlpatterns = [
    path("address/", ProfileAddressView.as_view()),
]
urlpatterns += router.urls