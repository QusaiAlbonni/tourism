from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagsCategoryViewSet, TagViewSet

router = DefaultRouter()
router.register(r'categories', TagsCategoryViewSet)
router.register(r'', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]