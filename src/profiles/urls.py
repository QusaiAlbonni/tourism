from django.urls import path
from django.urls import re_path, include
from .views import CreditCardCreateView,CreditCardRetrieveAPIView,CreditCardDeleteView,PointsWalletRetrieveAPIView,ProfileAddressView, ProfileViewSet, ExchangeRatesView,UserIPCurrencyView
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
    path('get_currency/', UserIPCurrencyView.as_view(), name='get_currency'),
]
urlpatterns += router.urls