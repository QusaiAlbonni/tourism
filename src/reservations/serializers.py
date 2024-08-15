from rest_framework import serializers
from .models import TicketPurchase, PointsPayment, Payment
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import ValidationError
from activities.models import Ticket
from decimal import Decimal
from django.db import models
from djmoney.money import Money

class TicketPurchaseSerializer(serializers.ModelSerializer):
    use_points_discount = serializers.BooleanField(write_only= True, required= True)
    activity_type       = serializers.SerializerMethodField()
    activity_id         = serializers.SerializerMethodField()
    refund_rate         = serializers.SerializerMethodField()
    payment             = serializers.SerializerMethodField()
    payment_currency    = serializers.SerializerMethodField()
    activity_name       = serializers.SerializerMethodField()
    class Meta:
        model = TicketPurchase
        fields= ['id','use_points_discount','ticket_id','canceled', 'refunded','refund_rate','payment','payment_currency', 'activity_name','refundable', 'can_be_canceled', 'activity_id', 'activity_type', 'ticket', 'owner','qr_code', 'scanned', 'scan_date', 'uuid', 'created', 'modified', 'scanable']
        read_only_fields = ['ticket', 'owner', 'scanned','refundable','qr_code', 'can_be_canceled', 'canceled', 'refunded', 'scan_date', 'uuid', 'created', 'modified', 'scanable', 'refund_rate','payment', 'payment_currency', 'activity_name']
    
    def create(self, validated_data):
        ticket_pk = self.context.get('ticket_pk', None)
        if ticket_pk:
            validated_data['ticket_id'] = ticket_pk
        validated_data['owner_id']  = self.context['owner']
        use_points_discount = validated_data.pop('use_points_discount')
        
        try:
            instance = self.Meta.model(**validated_data)
            instance.save(use_points_discount=use_points_discount)
        except DjangoValidationError as e:
            raise ValidationError(dict(e))
        return instance
    def get_activity_type(self, obj: TicketPurchase):
        return obj.ticket.get_activity_type()
    def get_activity_id(self, obj: TicketPurchase):
        return obj.ticket.activity.pk
    def get_refund_rate(self, obj: TicketPurchase):
        if obj.forced_refundable():
            return Decimal('100.0')
        return obj.ticket.activity.refund_rate
    def get_payment(self, obj: TicketPurchase):
        total_payments = obj.payments.aggregate(total_sum=models.Sum('amount'))['total_sum']
        return total_payments
    def get_payment_currency(self, obj: TicketPurchase):
        return obj.payments.first().amount.currency.code
    def get_activity_name(self, obj: TicketPurchase):
        return obj.ticket.activity.name
    
class ScanQRCodeSerializer(serializers.ModelSerializer):
    uuid     = serializers.UUIDField()
    ticket_id= serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all(), write_only=True, source='ticket', allow_null=False)

    class Meta:
        model = TicketPurchase
        fields = ['uuid', 'ticket_id']

    def validate_uuid(self, value):
        try:
            instance = self.Meta.model.objects.get(uuid=value)
        except self.Meta.model.DoesNotExist:
            raise serializers.ValidationError("Instance with this UUID does not exist.")

        return value
    
    