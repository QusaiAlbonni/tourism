from django.shortcuts import render
from django.http import Http404
from .serializers import ProfileSerializer, ProfileAddressCreateSerializer, CreditCardSerializer,PointsWalletSerializer
from rest_framework import generics, status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, MethodNotAllowed, NotFound
from .models import Profile, CreditCard,PointsWallet
from address.models import Address
from djmoney.contrib.exchange.models import Rate
from .serializers import RateSerializer
from django.utils.translation import gettext_lazy as _



class CreditCardCreateView(generics.CreateAPIView):
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CreditCardRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user'

    def get_object(self):
        user = self.request.user
        try:
            return CreditCard.objects.get(user=user)
        except CreditCard.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'detail': _('This user does not have any credit card.')}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CreditCardDeleteView(generics.DestroyAPIView):
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user'
    def get_object(self):
        user = self.request.user
        try:
            return CreditCard.objects.get(user=user)
        except CreditCard.DoesNotExist:
            return None
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'detail': _('This user does not have any credit card.')}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PointsWalletRetrieveAPIView(generics.RetrieveAPIView):

    serializer_class = PointsWalletSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user'

    def get_object(self):
        user = self.request.user
        return PointsWallet.objects.get(user=user)
    def get_object(self):
        user = self.request.user
        try:
            return PointsWallet.objects.get(user=user)
        except PointsWallet.DoesNotExist:
            raise Http404("PointsWallet does not exist for this user.")
 


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        query_set= super().get_queryset()
        if self.request.user.is_admin or self.request.user.is_superuser:
            return query_set
        else:
            return query_set.filter(user= self.request.user)

    def get_instance(self):
        return self.request.user.profile
    
    def create(self, request):
        raise MethodNotAllowed("POST")
    
    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    
class ProfileAddressView(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.CreateModelMixin,
                        generics.GenericAPIView):
    
    queryset = Address.objects.all()
    serializer_class = ProfileAddressCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_instance(self):
        return self.request.user.profile.address
     
    def create(self, request, *args, **kwargs):
        address = self.get_instance()
        if address:
            raise ValidationError({'detail':_('address already exists')})
        return super().create(request, *args, **kwargs)
    
    
    def get(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        address = self.get_instance()
        if address is None:
            raise NotFound({'detail':_('address does not exist')})
        return self.retrieve(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.partial_update(request, *args, **kwargs)
    
class ExchangeRatesView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Rate.objects.all()
    serializer_class= RateSerializer
    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

import ipapi
# myapp/views.py
# myapp/views.py
import requests
from django.http import JsonResponse
from django.views import View
import json
class UserIPCurrencyView(View):
    def get(self, request, *args, **kwargs):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        x_real_ip = request.META.get('HTTP_X_REAL_IP')

        if x_forwarded_for:
            print(1)
            ip = x_forwarded_for.split(',')[0]
        elif x_real_ip:
            print(2)
            ip = x_real_ip
        else:
            print(3)
            ip = request.META.get('REMOTE_ADDR')

        print(ip)
        
        # ip = '8.8.8.8'

        ipapi.location()
        location_data = ipapi.location(ip)
        print(location_data)
        return JsonResponse(location_data)