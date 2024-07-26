from rest_framework import viewsets
from .models import Event,EventPeriodicTask
from .serializers import EventSerializer
from rest_framework.exceptions import MethodNotAllowed
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import CanManageEventOrReadOnly
from django.shortcuts import render, get_object_or_404

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # permission_classes = [CanManageEventOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']
    
    # def get_queryset(self):
    #     return EventPeriodicTask.objects.prefetch_related("periodic_tasks")
    #     return Event.objects.prefetch_related('periodic_tasks') 
    
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    
    def perform_destroy(self, instance):
        event_periodic_tasks = EventPeriodicTask.objects.filter(event=instance)
        print(instance.id)
        for event_periodic_task in event_periodic_tasks:
            event_periodic_task.periodic_task.delete()
            event_periodic_task.delete()
        instance.delete()
