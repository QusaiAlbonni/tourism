# from .views import ScheduledTaskAPIView
# path('scheduled-tasks/', ScheduledTaskAPIView.as_view(), name='scheduled-tasks'),

from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'service-photos', views.ServicePhotoViewSet)
# router.register(r'services', views.ServiceViewSet)  
router.register(r'service-favorites', views.ServiceFavoriteViewSet)
router.register(r'service-reviews', views.ServiceReviewViewSet)
router.register(r'service-discounts', views.ServiceDiscountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]