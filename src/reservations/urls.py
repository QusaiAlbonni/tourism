from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import TicketPurchaseViewSet

router = DefaultRouter()

router.register(r'purchases', TicketPurchaseViewSet, "ticket-purchases-raw")

urlpatterns = [
    
] + router.urls
