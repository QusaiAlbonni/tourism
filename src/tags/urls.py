from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagsCategoryViewSet, TagViewSet
from rest_framework_nested.routers import NestedSimpleRouter


router = DefaultRouter()
router.register(r'categories', TagsCategoryViewSet)
router.register(r'', TagViewSet)

# categories_router = NestedSimpleRouter(router, r'categories', lookup='category')
# categories_router = NestedSimpleRouter(router, r'categories', lookup='category')
# categories_router = NestedSimpleRouter(router, r'categories', lookup='category')
# categories_router.register(r'tags', TagViewSet, basename='category-tags')

urlpatterns = [
    path('', include(router.urls)),
]