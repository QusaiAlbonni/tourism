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
        fields= ['id','use_points_discount','ticket_id','canceled', 'refunded','refundable', 'can_be_canceled', 'activity_id', 'activity_type', 'ticket', 'owner','qr_code', 'scanned', 'scan_date', 'uuid', 'created', 'modified']
        read_only_fields = ['ticket', 'owner', 'scanned','refundable','qr_code', 'can_be_canceled', 'canceled', 'refunded', 'scan_date', 'uuid', 'created', 'modified']
    
    def create(self, validated_data):
        ticket_pk = self.context.get('ticket_pk', None)
        if ticket_pk:
            validated_data['ticket_id'] = ticket_pk
        validated_data['owner_id']  = self.context['owner']
        use_points_discount = validated_data.pop('use_points_discount')
        
        try:
            instance = self.Meta.model(**validated_data)
            instance.save(use_points_discount=use_points_discount)
            print("hewe")
        except DjangoValidationError as e:
            raise ValidationError(dict(e))
        return instance
    def get_activity_type(self, obj: TicketPurchase):
        return obj.ticket.get_activity_type()
    def get_activity_id(self, obj: TicketPurchase):
        return obj.ticket.activity.pk
    
class ScanQRCodeSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()

    class Meta:
        model = TicketPurchase

    def validate_uuid(self, value):
        try:
            instance = self.Meta.model.objects.get(uuid=value)
        except self.Meta.model.DoesNotExist:
            raise serializers.ValidationError("Instance with this UUID does not exist.")

        return value
    
    