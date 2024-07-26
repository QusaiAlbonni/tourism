from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Service, ServicePhoto,ServiceFavorite,ServiceReview,ServiceDiscount
from django.db import IntegrityError
from app_auth.serializers import UserSerializer
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

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.refund_rate = validated_data.get('refund_rate', instance.refund_rate)
    #     instance.upfront_rate = validated_data.get('upfront_rate', instance.upfront_rate)
    #     instance.allow_points = validated_data.get('allow_points', instance.allow_points)
    #     instance.allow_review = validated_data.get('allow_review', instance.allow_review)
    #     instance.points_gift = validated_data.get('points_gift', instance.points_gift)
    #     instance.save()
    #     return instance
       
    
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
        print(service)
        # s=Service.objects.all(service=service)
        if not service.allow_review:
            raise serializers.ValidationError("You cant review this service.")
        if ServiceReview.objects.filter(user=user, service=service).exists():#and should put the reserv if
            raise serializers.ValidationError("You have already review this service.")
        
        service_review = ServiceReview.objects.create(user=user, **validated_data)
        return service_review

class ServiceDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDiscount
        fields = ['id', 'service', 'event', 'percent', 'created', 'modified']
    def create(self, validated_data):
           try:
               return super().create(validated_data)
           except IntegrityError as e:
               raise serializers.ValidationError({"detail": "Service with this event already exists or service with null event already exists."})