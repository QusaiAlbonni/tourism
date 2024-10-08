from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Service, ServicePhoto,ServiceFavorite,ServiceReview,ServiceDiscount
from django.db import IntegrityError
from app_auth.serializers import UserSerializer
from events.models import Event
class ServicePhotoSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        write_only=True,
        required=False
    )
    class Meta:
        model = ServicePhoto
        fields = ['id', 'image','service']
        # read_only_fields
    def create(self, validated_data):
        service = validated_data.pop('service')
        try:
            service_photo = ServicePhoto.objects.create(service=service, **validated_data)
        except ValidationError as e:
            raise serializers.ValidationError({'detail': str(e)})
        return service_photo

class ServiceSerializer(serializers.ModelSerializer):
    photos = ServicePhotoSerializer(many=True,required=False)
    avg_rating = serializers.ReadOnlyField()
    num_rating = serializers.ReadOnlyField()
    discount = serializers.ReadOnlyField()
    on_discount = serializers.ReadOnlyField()
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'refund_rate', 'upfront_rate','points_gift', 'allow_points','allow_review', 'photos','avg_rating','num_rating','discount','on_discount']
    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])

        if len(photos_data) < 2:
            raise serializers.ValidationError("At least two photos are required.")
        if len(photos_data)>7:
            raise serializers.ValidationError("At most 7 photos.")

        service = self.Meta.model.objects.create(**validated_data)

        for photo_data in photos_data:
            photo_data['service'] = service
            ServicePhotoSerializer(data=photo_data).create(photo_data)

        return service 
       
    
class ServiceFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFavorite
        fields = ['id', 'service','user', 'created', 'modified']
        read_only_fields = ['user','created', 'modified']

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        if ServiceFavorite.objects.filter(user=user, service=service).exists():
            raise serializers.ValidationError("You have already favorited this service.")
        service_favorite = ServiceFavorite.objects.create(user=user, **validated_data)
        return service_favorite
    
  
class ServiceReviewSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    user_name = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = ServiceReview
        fields = ['id','service','rating', 'user','user_name', 'comment','created']
        read_only_fields = ['user','created', 'updated']

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        # s=Service.objects.all(service=service)
        if not service.allow_review:
            raise serializers.ValidationError("You cant review this service.")
        if ServiceReview.objects.filter(user=user, service=service).exists():#and should put the reserv if
            raise serializers.ValidationError("You have already review this service.")
        
        service_review = ServiceReview.objects.create(user=user, **validated_data)
        return service_review

class ServiceDiscountSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(),required=False, allow_null=True)
    type = serializers.ReadOnlyField()
    class Meta:
        model = ServiceDiscount
        fields = ['id', 'service', 'event', 'percent','type', 'created', 'modified']

    def create(self, validated_data):
           
           try:
               return super().create(validated_data)
           except Exception  as e:
               raise serializers.ValidationError({"detail": str(e)})