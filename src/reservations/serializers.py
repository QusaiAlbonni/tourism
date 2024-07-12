from rest_framework import serializers
from .models import TicketPurchase, PointsPayment, Payment
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import ValidationError

class TicketPurchaseSerializer(serializers.ModelSerializer):
    use_points_discount = serializers.BooleanField(write_only= True, required= True)
    class Meta:
        model = TicketPurchase
        fields= ['use_points_discount','ticket_id', 'ticket', 'owner', 'scanned', 'scan_date', 'uuid', 'created', 'modified']
        read_only_fields = ['ticket', 'owner', 'scanned', 'scan_date', 'uuid', 'created', 'modified']
    
    def create(self, validated_data):
        validated_data['ticket_id'] = self.context['ticket_pk']
        validated_data['owner_id']  = self.context['owner']
        use_points_discount = validated_data.pop('use_points_discount')
        try:
            instance = super().create(validated_data)
        except DjangoValidationError as e:
            raise ValidationError(str(e))
        return instance
    def cancel(self):
        pass
    
    