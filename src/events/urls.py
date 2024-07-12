# from .views import ScheduledTaskAPIView
# path('scheduled-tasks/', ScheduledTaskAPIView.as_view(), name='scheduled-tasks'),

from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.EventViewSet)


urlpatterns = [
    path('', include(router.urls)),
]