from django.shortcuts import render
from rest_framework .generics import CreateAPIView,RetrieveAPIView,DestroyAPIView
from .serializers import CreditCardSerializer,PointsWalletSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import  status
from rest_framework.response import Response
from .models import CreditCard,PointsWallet
from django.http import Http404
from .serializers import ProfileSerializer, ProfileAddressCreateSerializer
from rest_framework import generics, status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, MethodNotAllowed, NotFound
from .models import Profile
from address.models import Address



class CreditCardCreateView(CreateAPIView):
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CreditCardRetrieveAPIView(RetrieveAPIView):
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
            return Response({'detail': 'This user does not have any credit card.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CreditCardDeleteView(DestroyAPIView):
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
            return Response({'detail': 'This user does not have any credit card.'}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PointsWalletRetrieveAPIView(RetrieveAPIView):

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
            raise ValidationError({'detail':'address already exists'})
        return super().create(request, *args, **kwargs)
    
    
    def get(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        address = self.get_instance()
        if address is None:
            raise NotFound({'detail':'address does not exist'})
        return self.retrieve(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.partial_update(request, *args, **kwargs)
