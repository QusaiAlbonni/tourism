from django.http import Http404

from django.shortcuts import render
from .serializers import TicketPurchaseSerializer, TicketPurchase
from activities.models import Ticket
from rest_framework.viewsets import ModelViewSet
from app_auth.permissions import IsOwner, CanManageActivities, isAdmin, ReadOnly
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _

class TicketPurchaseViewSet(ModelViewSet):
    serializer_class = TicketPurchaseSerializer
    permission_classes = [(IsAuthenticated & IsOwner) | (CanManageActivities & ReadOnly)]
    
    def get_queryset(self):
        query = TicketPurchase.objects.filter(ticket= self.kwargs['ticket_pk'])
        user = self.request.user
        if self.action == "list" and not (user.is_staff or user.is_admin):
            query.filter(owner= user)
        return query
            
    def get_serializer_context(self):   
        context = super().get_serializer_context()
        context['ticket_pk'] = self.kwargs['ticket_pk']
        context['owner'] = self.request.user.id
        return context
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Ticket.DoesNotExist as e:
            raise Http404(_("Ticket does not exist."))
    def cancel(self):
        pass
    
    def destroy(self, request, *args, **kwargs):
        raise Http404()
    
    def update(self, request, *args, **kwargs):
        raise Http404()
    
    def partial_update(self, request, *args, **kwargs):
        raise Http404()
    

