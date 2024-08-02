from rest_framework import viewsets
from .serializers import (
    PropertySerializer, SupPropertySerializer, SupPropertyBedSerializer,
    SupPropertyPhotoSerializer, PropertyTagSerializer, SupPropertyTagSerializer
)
from .models import (
    Property, SupProperty, SupPropertyBed, SupPropertyPhoto, PropertyTag, SupPropertyTag
)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class SupPropertyViewSet(viewsets.ModelViewSet):
    queryset = SupProperty.objects.all()
    serializer_class = SupPropertySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['property_id']
    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied('there is no partial update to supproperty')

class SupPropertyBedViewSet(viewsets.ModelViewSet):
    queryset = SupPropertyBed.objects.all()
    serializer_class = SupPropertyBedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['supproperty']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        supproperty = instance.supproperty
        supproperty_type = supproperty.type
        
        # Retrieve all bed types with the same supproperty.id except the current instance
        bed_types = SupPropertyBed.objects.filter(supproperty=supproperty).exclude(id=instance.id).values_list('type', flat=True)
        
        if supproperty_type == 'Suite' and 'King' not in bed_types:
            raise ValidationError("A Suite must have at least one King bed.")
        
        if supproperty_type == 'Family':
            if not any(bed in bed_types for bed in ['Single', 'Double', 'King']):
                raise ValidationError("A Family room must have at least one of Single, Double, or King bed.")
            if not any(bed in bed_types for bed in ['Cheldren', 'DoubleCheldren']):
                raise ValidationError("A Family room must have at least one of Cheldren or DoubleCheldren bed.")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SupPropertyPhotoViewSet(viewsets.ModelViewSet):
    queryset = SupPropertyPhoto.objects.all()
    serializer_class = SupPropertyPhotoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['property']
class PropertyTagViewSet(viewsets.ModelViewSet):
    queryset = PropertyTag.objects.all()
    serializer_class = PropertyTagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['property']
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return response
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        raise PermissionDenied()

    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied()

    
class SupPropertyTagViewSet(viewsets.ModelViewSet):
    queryset = SupPropertyTag.objects.all()
    serializer_class = SupPropertyTagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['supproperty']
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return response
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        raise PermissionDenied()

    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied()