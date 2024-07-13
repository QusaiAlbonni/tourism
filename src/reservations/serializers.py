from rest_framework import serializers
from .models import TicketPurchase, PointsPayment, Payment
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import ValidationError

class TicketPurchaseSerializer(serializers.ModelSerializer):
    use_points_discount = serializers.BooleanField(write_only= True, required= True)
    activity_type       = serializers.SerializerMethodField()
    activity_id         = serializers.SerializerMethodField()
    class Meta:
        model = TicketPurchase
        fields= ['use_points_discount','ticket_id', 'activity_id', 'activity_type', 'ticket', 'owner', 'scanned', 'scan_date', 'uuid', 'created', 'modified']
        read_only_fields = ['ticket', 'owner', 'scanned', 'scan_date', 'uuid', 'created', 'modified']
    
    def create(self, validated_data):
        ticket_pk = self.context.get('ticket_pk', None)
        if ticket_pk:
            validated_data['ticket_id'] = ticket_pk
        validated_data['owner_id']  = self.context['owner']
        use_points_discount = validated_data.pop('use_points_discount')
        try:
            instance = TicketPurchase(**validated_data)
            instance.save(use_points_discount=use_points_discount)
        except DjangoValidationError as e:
            raise ValidationError(dict(e))
        return instance
    def cancel(self):
        pass
    def get_activity_type(self, obj: TicketPurchase):
        return obj.ticket.get_activity_type()
    def get_activity_id(self, obj: TicketPurchase):
        return obj.ticket.activity.pk
    
    