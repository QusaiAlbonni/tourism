from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import ValidationError, MethodNotAllowed, NotFound
from app_auth.permissions import isAdminOrReadOnly
from .models import Guide
from .serializers import GuideSerializer

from .models import activitestag
from .serializers import activitetagSerializer

class activitetagViewSet(viewsets.ModelViewSet):
    queryset = activitestag.objects.all()
    serializer_class = activitetagSerializer


class GuideViewSet(viewsets.ModelViewSet):
    serializer_class = GuideSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, isAdminOrReadOnly]
    def get_queryset(self):
        return Guide.objects.all()
    
    @action(["post"], detail=True, permission_classes= [IsAuthenticated])
    def toggle_like(self, request, pk):
        guide = self.get_object()
        liked = guide.toggle_like(self.request.user)
        return Response({ "liked": liked }, status=status.HTTP_200_OK)