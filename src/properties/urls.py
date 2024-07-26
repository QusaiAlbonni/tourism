from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, SupPropertyViewSet, SupPropertyBedViewSet,
    SupPropertyPhotoViewSet, PropertyTagViewSet, SupPropertyTagViewSet
)

router = DefaultRouter()

router.register(r'sup-properties', SupPropertyViewSet)
router.register(r'sup-property-beds', SupPropertyBedViewSet)
router.register(r'sup-property-photos', SupPropertyPhotoViewSet)
router.register(r'property-tags', PropertyTagViewSet)
router.register(r'sup-property-tags', SupPropertyTagViewSet)
router.register(r'', PropertyViewSet)                                                   

urlpatterns = [
    path('', include(router.urls)),
]   