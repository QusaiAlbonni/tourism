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
from .f import PropertyFilter

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class= PropertyFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        max_price = self.request.query_params.get('max_price')
        min_price = self.request.query_params.get('min_price')
        children_capacity = self.request.query_params.get('children_capacity')
        adults_capacity = self.request.query_params.get('adults_capacity')
        start_date = self.request.query_params.get('reservation_period_after')
        end_date = self.request.query_params.get('reservation_period_before')
        if max_price is not None:
            context['max_price'] = int(max_price)
        if min_price is not None:
            context['min_price'] = int(min_price)
        if adults_capacity is not None:
            context['adults_capacity'] = int(adults_capacity)
        if children_capacity is not None and adults_capacity is None:
            raise ValidationError({
            'error': 'children_capacity cant be without adults_capacity.'
        })
        if children_capacity is not None :
            context['children_capacity'] = int(children_capacity)       
        if (start_date and not end_date) or (end_date and not start_date):
            raise ValidationError({
            'error': 'should put both start_date and end_date not one.'
        })
        if start_date is not None:
            context['start_date'] = int(start_date)
        if end_date is not None :
            context['end_date'] = int(end_date)

        return context
    

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