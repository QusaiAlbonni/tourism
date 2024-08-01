from django.shortcuts import render
from .serializers import NotificationSerializer, Notification
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework import status
# Create your views here.



class NotificationsViewSet(mixins.ListModelMixin,GenericViewSet):
    permission_classes= [IsAuthenticated]
    serializer_class= NotificationSerializer
    
    def get_queryset(self) -> QuerySet:
        return self.request.user.notifications.all()
    
    
    @action(methods=('post',), detail=False)
    def mark_all_as_read(self, request):
        queryset = self.get_queryset()
        queryset.mark_all_as_read()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(methods=('post',), detail=False)
    def mark_all_as_unread(self, request):
        queryset = self.get_queryset()
        queryset.mark_all_as_unread()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=('post',), detail=True)
    def mark_as_read(self, request, pk):
        queryset = self.get_object()
        queryset.mark_as_read()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=('post',), detail=True)
    def mark_as_unread(self, request, pk):
        queryset = self.get_object()
        queryset.mark_as_unread()
        
        return Response(status=status.HTTP_204_NO_CONTENT)