from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagsCategoryViewSet,TagViewSet,TagsCategoryPermissionViewSet

router = DefaultRouter()
router.register(r'tagscategories', TagsCategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'tagpermission', TagsCategoryPermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]