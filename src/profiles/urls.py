from django.urls import path
from django.urls import path, re_path, include
from .views import ProfileAddressList, ProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", ProfileViewSet)

urlpatterns = [
    path("address/", ProfileAddressList.as_view())
]
urlpatterns += router.urls