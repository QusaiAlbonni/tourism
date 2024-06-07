from rest_framework import serializers
from .models import Guide, Activity, Site, Ticket, Tour, Attraction
from services.serializers import ServicePhotoSerializer
from services.serializers import ServiceSerializer, ServiceReviewSerializer
from address.models import Address


class GuideSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    class Meta:
        model = Guide
        fields = [
            'id',
            'name',
            'bio',
            'avatar',
            'likes',
            'email',
            'liked',
            'is_popular'
        ]
        read_only_fields = ('likes', 'liked')
    def get_liked(self, obj : Guide) -> bool:
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.is_liked_by_user(user)
        return False
    
class AddressSerializer(serializers.ModelSerializer):
    locality    = serializers.CharField(max_length=165, allow_blank=True, required=False)
    postal_code = serializers.CharField(max_length=10, allow_blank=True, required=False)
    state       = serializers.CharField(max_length=165, allow_blank=True, required=False)
    state_code  = serializers.CharField(max_length=8, allow_blank=True, required=False)
    country     = serializers.CharField(max_length=40, allow_blank=True, required=False)
    country_code= serializers.CharField(max_length=2, allow_blank=True, required=False)
    
    class Meta:
        model = Address
        fields = [
            'id',
            'raw',
            'street_number',
            'route',
            'locality',
            'postal_code',
            'state',
            'state_code',
            'country',
            'country_code',
        ]

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ticket
        fields =['activity_id','name', 'description','price_currency', 'price', 'price_in_points', 'points_rate', 'valid_until', 'created', 'modified']
        read_only_fields = ['created', 'modified', 'activity']
    def create(self, validated_data):
        validated_data['activity_id'] = self.context['activity_pk']
        return super().create(validated_data)


class SiteSerializer(ServiceSerializer):
    address = AddressSerializer(required=True)
    tickets = TicketSerializer(read_only=True, many=True)
    class Meta:
        model = Site
        fields = ['id','name', 'description', 'refund_rate', 'allow_points', 'photos', 'address', 
                'opens_at', 'work_hours', 'closes_at','created', 'modified', 'review_by', 'tickets', ]
        read_only_fields = ['created', 'modified', 'tickets']
        
    def create(self, validated_data):
        validated_data['upfront_rate'] = 100
        site = super().create(validated_data)
        address = validated_data['address']
        site.address = address
        site.save()
        return site
    def update(self, instance, validated_data):
        address = validated_data.pop('address')
        instance= super().update(instance, validated_data)
        instance.address = address
        instance.save()
        return instance
    
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields= '__all__'
        

class AttractionSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)
    class Meta:
        model = Attraction
        fields = ['address', 'name', 'order', 'photo']
        read_only_fields = ['created', 'modified', 'order']
    def create(self, validated_data):
        address = validated_data.pop('address')
        
        validated_data['tour_id'] = self.context['tour_pk']
        
        validated_data['order'] = self.get_order()
        attraction = super().create(validated_data)
        
        attraction.address = address
        attraction.save()
        
        return attraction
    def update(self, instance, validated_data):
        address = validated_data.pop('address')
        
        instance= super().update(instance, validated_data)
        
        instance.address = address
        instance.save()
        
        return instance
    def get_order(self):
        last_order =Attraction.objects.filter(tour= self.context['tour_pk']).order_by('order').first()
        if last_order == None:
            order = 1
        else:
            order= last_order.order + 1
        return order
    
class TourSerializer(ServiceSerializer):
    attractions = AttractionSerializer(many=True, read_only=True)
    guide       = GuideSerializer(read_only=True)
    guide_id    = serializers.PrimaryKeyRelatedField(queryset=Guide.objects.all(), write_only=True, source='guide', allow_null=False)
    tickets     = TicketSerializer(read_only= True, many=True)
    class Meta:
        model = Tour
        fields = ServiceSerializer.Meta.fields + ['tickets','guide_id','guide','takeoff_date','end_date', 'end_date', 'attractions', 'duration']
        read_only_fields = ['created', 'modified', 'tickets', 'guide']