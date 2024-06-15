import datetime
from rest_framework import serializers
from .models import Guide, Activity, Site, Ticket, Tour, TourSite, Listing
from services.serializers import ServiceSerializer
from address.models import Address
from django.db import IntegrityError
from django.db import models
from rest_framework.exceptions import ValidationError


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
        fields =['id','activity_id','name', 'description','stock','price_currency', 'price', 'price_in_points', 'points_rate', 'valid_until', 'created', 'modified']
        read_only_fields = ['created', 'modified', 'activity']
    def create(self, validated_data):
        validated_data['activity_id'] = self.context['activity_pk']
        return super().create(validated_data)


class SiteSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True, allow_null= False)
    class Meta:
        model = Site
        fields = ['id','name', 'description', 'photo', 'address', 
        'created', 'modified']
        read_only_fields = ['created', 'modified']
        
    def create(self, validated_data):
        address = validated_data.pop('address')
        site = super().create(validated_data)
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
        

class TourSiteSerializer(serializers.ModelSerializer):
    site_id = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all(), write_only=True, source='site', allow_null=False)
    site    = SiteSerializer(read_only= True)
    class Meta:
        model = TourSite
        fields = ['id', 'order', 'site_id', 'site', 'tour']
        read_only_fields = ['created', 'modified', 'order', 'site', 'tour']
    
    def create(self, validated_data):
        
        validated_data['tour_id'] = self.context['tour_pk']
        
        validated_data['order'] = self._get_order()
        try:
            attraction = super().create(validated_data)
        except IntegrityError as e:
            raise ValidationError({"detail":"duplicate entry for the site"})
        return attraction
    
    def update(self, instance, validated_data):
        try:
            instance= super().update(instance, validated_data)
        except IntegrityError as e:
            raise ValidationError({"detail":"duplicate entry for the site"})
        return instance
    
    def _get_order(self):
        last_order =TourSite.objects.filter(tour= self.context['tour_pk']).order_by('-order').first()
        if last_order == None:
            order = 1
        else:
            order= last_order.order + 1
        return order
    
class TourSerializer(ServiceSerializer):
    sites       = TourSiteSerializer(many=True, read_only=True, source= 'tour_sites')
    guide       = GuideSerializer(read_only=True)
    guide_id    = serializers.PrimaryKeyRelatedField(queryset=Guide.objects.all(), write_only=True, source='guide', allow_null=False)
    tickets     = TicketSerializer(read_only= True, many=True)
    class Meta:
        model = Tour
        fields = ServiceSerializer.Meta.fields + ['sites','tickets','guide_id','guide','takeoff_date','end_date', 'end_date', 'duration']
        read_only_fields = ['created', 'modified', 'tickets', 'guide', 'upfront_rate']
    
    def create(self, validated_data):
        validated_data['upfront_rate'] = 100
        return super().create(validated_data)

    def validate(self, data):
        takeoff_date = data.get('takeoff_date')
        duration = data.get('duration')
        guide = data.get('guide')

        if not (takeoff_date and duration and guide):
            raise serializers.ValidationError("Takeoff date, duration, and book are required.")

        input_end_date = takeoff_date + duration

        overlapping_records = Tour.objects.annotate(
            end_date=models.ExpressionWrapper(models.F('takeoff_date') + models.F('duration'), output_field=models.DateTimeField())
        ).filter(
            models.Q(guide=guide) &
            models.Q(takeoff_date__lt=input_end_date) &
            models.Q(end_date__gt=takeoff_date)
        )

        if self.instance:
            overlapping_records = overlapping_records.exclude(id=self.instance.id)

        if overlapping_records.exists():
            raise serializers.ValidationError({"guide_id":"The specified time range overlaps with an existing tour for this guide."})
        return super().validate(data)

class ListingSerializer(ServiceSerializer):
    tickets = TicketSerializer(read_only=True, many=True)
    site    = SiteSerializer(read_only=True)
    site_id = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all(), write_only=True, source='site', allow_null=False)
    class Meta:
        model = Listing
        fields = ['id','name', 'description', 'refund_rate', 'allow_points', 'photos', 'site', 
                'opens_at', 'work_hours', 'closes_at','created', 'modified', 'review_by', 'tickets', 'site_id', 'website']
        read_only_fields = ['created', 'modified', 'tickets']
    def create(self, validated_data):
        validated_data['upfront_rate'] = 100
        return super().create(validated_data)
    def validate(self, data):
        opens_at = data.get('opens_at')
        work_hours = data.get('work_hours')
        opens_at_datetime = datetime.datetime.combine(datetime.datetime.today(), opens_at)

        work_hours_int = int(work_hours)
        work_minutes = (work_hours - work_hours_int) * 60

        closing_time = opens_at_datetime + datetime.timedelta(hours=work_hours_int, minutes=float(work_minutes))

        if closing_time.time() < opens_at:
            raise ValidationError("The sum of opens_at and work_hours exceeds 24 hours.")
        return super().validate(data)
        