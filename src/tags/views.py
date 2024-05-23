from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import TagsCategory, Tag
from .serializers import TagsCategorySerializer, TagSerializer
from django.apps import apps
from app_auth.permissions import isAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
    

class TagsCategoryViewSet(viewsets.ModelViewSet):
    queryset = TagsCategory.objects.all()
    serializer_class = TagsCategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

