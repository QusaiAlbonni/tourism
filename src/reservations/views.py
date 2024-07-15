from django.http import Http404
from django.core.exceptions import ValidationError as DjValidationError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .serializers import TicketPurchaseSerializer, TicketPurchase, ScanQRCodeSerializer
from activities.models import Ticket
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from app_auth.permissions import IsOwner, CanManageActivities, isAdmin, ReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from django.utils.translation import gettext_lazy as _
from .exceptions import NonRefundableError, NonRefundableException, CantBeCanceled, CantBeCanceledError
from django.shortcuts import get_object_or_404
from .permissions import CanScanReservations
from django.db import transaction

class TicketPurchaseViewSet(ModelViewSet):
    serializer_class = TicketPurchaseSerializer
    permission_classes = [(IsAuthenticated & IsOwner) | (CanManageActivities & ReadOnly)]
    
    def get_queryset(self):
        ticket_pk = self.kwargs.get('ticket_pk', None)
        if ticket_pk:
            query = self.serializer_class.Meta.model.objects.filter(ticket= self.kwargs['ticket_pk'])
        else:
            query = self.serializer_class.Meta.model.objects.all()
        user = self.request.user
        print(user)
        if self.action == "list" and not (user.is_staff or user.is_admin or user.has_perm('app_auth.manage_activities')):
            query = query.filter(owner= user)
        return query
            
    def get_serializer_context(self):   
        context = super().get_serializer_context()
        if 'ticket_pk' in self.kwargs:
            context['ticket_pk'] = self.kwargs['ticket_pk']
        context['owner'] = self.request.user.id
        return context
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Ticket.DoesNotExist as e:
            raise Http404(_("Ticket does not exist."))
        
    @action(('post',), detail=True)
    def cancel(self, request, pk, *args, **kwargs):
        instance = self.get_queryset().get(pk=pk)
        if not instance:
            raise Http404(_("purchase object not found."))
        try:
            instance.cancel()
        except CantBeCanceled as e:
            raise CantBeCanceledError()
        serializer = self.serializer_class(instance, read_only=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    
    @action(('post',), detail=True)
    def refund(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if not instance:
            raise Http404(_("purchase object not found."))
        try:
            instance.refund()
        except NonRefundableException as e:
            raise NonRefundableError()
        serializer = self.serializer_class(instance, read_only=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed()
    
class QrReservationViewSet(GenericViewSet):
    serializer_class  = ScanQRCodeSerializer
    permission_classes= [CanScanReservations] 
    def get_queryset(self):
        return ScanQRCodeSerializer.Meta.model.objects.all()
    def get_object(self):
        uuid = self.kwargs['uuid']
        return get_object_or_404(self.get_queryset().filter(uuid= uuid))
    @action(('post',), detail=False)
    def scan(self, request, *args, **kwargs):
        serializer = ScanQRCodeSerializer(data={'uuid': self.kwargs['uuid']})
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        try:
            instance.clean_scan()
            instance.on_scan()
        except DjValidationError as e:
            raise ValidationError(str(e))
        return Response({'detail':'success'}, status.HTTP_200_OK)
            
    

