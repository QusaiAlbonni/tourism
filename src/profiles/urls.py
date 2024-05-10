from django.urls import path
from django.urls import path, re_path, include
from .views import CreditCardCreateView,CreditCardRetrieveAPIView,CreditCardDeleteView,PointsWalletRetrieveAPIView,ProfileAddressView, ProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", ProfileViewSet)

urlpatterns = [
    path("address/", ProfileAddressView.as_view()),
    path('credit/', include([
        path('create', CreditCardCreateView.as_view(), name='credit-card-create'),
        path('', CreditCardRetrieveAPIView.as_view(), name='credit-card-retrieve'),
        path('delete', CreditCardDeleteView.as_view(), name='credit-card-delete'),
    ])),
    path('wallet/', include([
        path('', PointsWalletRetrieveAPIView.as_view(), name='credit-card-retrieve'),
    ])),
]
urlpatterns += router.urls