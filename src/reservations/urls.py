from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import TicketPurchaseViewSet, QrReservationViewSet
router = DefaultRouter()

router.register(r'purchases/(?P<uuid>[0-9a-f-]+)', QrReservationViewSet, "ticket-purchase-scan")
router.register(r'purchases', TicketPurchaseViewSet, "ticket-purchases-raw")

urlpatterns = [
    
] + router.urls
