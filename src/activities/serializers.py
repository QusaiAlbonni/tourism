import datetime
from rest_framework import serializers
from .models import Guide, Activity, Site, Ticket, Tour, TourSite, Listing, ActivityTag
from services.serializers import ServiceSerializer
from address.models import Address
from django.db import IntegrityError
from django.db import models
from rest_framework.exceptions import ValidationError
from django.http import Http404
import django.utils.timezone as timezone
from django.utils.translation import gettext_lazy as _
from services.serializers import ServicePhotoSerializer
from tags.serializers import TagSerializer
from tags.models import Tag, TagsCategory
from django.shortcuts import get_object_or_404
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
            'formatted',
            'raw',
            'street_number',
            'route',
            'locality',
            'postal_code',
            'state',
            'state_code',
            'country',
            'country_code',
            'latitude',
            'longitude',
        ]
        read_only_fields= ['longitude', 'latitude']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ticket
        fields =['id','activity_id','name', 'description','stock','price_currency', 'price', 'points_discount_price', 'points_discount', 'valid_until', 'created', 'modified']
        read_only_fields = ['created', 'modified', 'activity']
    def create(self, validated_data):
        validated_data['activity_id'] = self.context['activity_pk']
        try:
            return super().create(validated_data)
        except Activity.DoesNotExist as e:
            raise Http404(_("Activity Does not exist."))
        
    def validate_valid_until(self, value):
        try:
            activity = Activity.objects.get(pk= self.context['activity_pk'])
        except Activity.DoesNotExist as e:
            raise Http404(_("Activity Does not exist."))
        if hasattr(activity, "tour"):
            ticket_activity_is_valid = activity.tour.takeoff_date.date() < value
            if not ticket_activity_is_valid:
                raise serializers.ValidationError(_("the Valid until field must be at least a day after than the takeoff date."))
            return value
        else:
            return value


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
    photos = ServicePhotoSerializer(many=True,required=False)
    class Meta:
        model = Activity
        fields= ServiceSerializer.Meta.fields + [ 'type', ]
        
    def get_type(self, obj : Activity):
        return obj.type
    
class ActivityTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True)
    tag_id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), write_only=True, source='tag', allow_null=False)
    class Meta:
        model = ActivityTag
        fields = ['id','activity', 'tag', 'tag_id']
        read_only_fields = ['activity', 'tag']
        
    def create(self, validated_data):
        
        validated_data['activity_id'] = self.context['activity_pk'] 
        
        get_object_or_404(Activity, pk= validated_data['activity_id'])
              
        try:
            try:
                activity_tag = super().create(validated_data)
            except (ValueError, IntegrityError) as e:
                raise ValidationError({"detail": str(e)})
        except Activity.DoesNotExist as e:
            raise Http404(_("Activity does not exist."))
        return activity_tag
    
    def update(self, instance, validated_data):
        get_object_or_404(Activity, pk= validated_data['activity_id'])
        
        try:
            instance= super().update(instance, validated_data)
        except (IntegrityError, ValueError) as e:
            raise ValidationError({"detail": str(e)})
        return instance
        

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
            try:
                attraction = super().create(validated_data)
            except IntegrityError as e:
                raise ValidationError({"detail":_("duplicate entry for the site")})
        except Tour.DoesNotExist as e:
            raise Http404(_("Tour does not exist."))
        return attraction
    
    def update(self, instance, validated_data):
        try:
            instance= super().update(instance, validated_data)
        except IntegrityError as e:
            raise ValidationError({"detail":_("duplicate entry for the site")})
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
    activity_tags        = ActivityTagSerializer(many=True, read_only=True)
    class Meta:
        model = Tour
        fields = ServiceSerializer.Meta.fields + ['activity_tags','sites','tickets','guide_id','guide','takeoff_date','end_date', 'end_date', 'duration']
        read_only_fields = ['created', 'modified', 'tickets', 'guide', 'upfront_rate']
    
    def create(self, validated_data):
        validated_data['upfront_rate'] = 100
        return super().create(validated_data)
    

    def validate(self, data):
        takeoff_date = data.get('takeoff_date')
        duration = data.get('duration')
        guide = data.get('guide')

        if not (takeoff_date and duration and guide):
            raise serializers.ValidationError(_("Takeoff date, duration, and book are required."))

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
            raise serializers.ValidationError({"guide_id":_("The specified time range overlaps with an existing tour for this guide.")})
        return super().validate(data)
    def update(self, instance, validated_data):
        validated_data.pop('photos', None)
        return super().update(instance, validated_data)

class ListingSerializer(ServiceSerializer):
    tickets = TicketSerializer(read_only=True, many=True)
    site    = SiteSerializer(read_only=True)
    site_id = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all(), write_only=True, source='site', allow_null=False)
    class Meta:
        model = Listing
        fields = [field for field in ServiceSerializer.Meta.fields if field != 'upfront_rate'] + [ 'site',
                'opens_at', 'work_hours', 'closes_at', 'tickets', 'site_id', 'website']
        read_only_fields = ['tickets']
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
            raise ValidationError(_("The sum of opens_at and work_hours exceeds 24 hours."))
        return super().validate(data)
    def update(self, instance, validated_data):
        validated_data.pop('photos', None)
        return super().update(instance, validated_data)
    

        