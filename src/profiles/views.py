from django.shortcuts import render
from .serializers import ProfileSerializer, ProfileAddressCreateSerializer
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from .models import Profile
from address.models import Address
# Create your views here.


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

    
class ProfileAddressList(generics.CreateAPIView):
    queryset = Address.objects.all()
    serializer_class = ProfileAddressCreateSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            return self.request.user.profile.address
        except Profile.DoesNotExist:
            raise ValidationError({'detail':'Profile does not exist'})
        
    def create(self, request, *args, **kwargs):
        address = self.get_queryset()
        if address:
            raise ValidationError({'detail':'address already exists'})
        return super().create(request, *args, **kwargs)