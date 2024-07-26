from rest_framework import viewsets
from .serializers import (
    PropertySerializer, SupPropertySerializer, SupPropertyBedSerializer,
    SupPropertyPhotoSerializer, PropertyTagSerializer, SupPropertyTagSerializer
)
from .models import (
    Property, SupProperty, SupPropertyBed, SupPropertyPhoto, PropertyTag, SupPropertyTag
)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class SupPropertyViewSet(viewsets.ModelViewSet):
    queryset = SupProperty.objects.all()
    serializer_class = SupPropertySerializer

class SupPropertyBedViewSet(viewsets.ModelViewSet):
    queryset = SupPropertyBed.objects.all()
    serializer_class = SupPropertyBedSerializer

class SupPropertyPhotoViewSet(viewsets.ModelViewSet):
    queryset = SupPropertyPhoto.objects.all()
    serializer_class = SupPropertyPhotoSerializer

class PropertyTagViewSet(viewsets.ModelViewSet):
    queryset = PropertyTag.objects.all()
    serializer_class = PropertyTagSerializer

class SupPropertyTagViewSet(viewsets.ModelViewSet):
    queryset = SupPropertyTag.objects.all()
    serializer_class = SupPropertyTagSerializer