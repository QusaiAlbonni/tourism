from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Service, ServicePhoto,ServiceFavorite,ServiceReview

class ServicePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePhoto
        fields = ['id','image']

    def create(self, validated_data):
        service = self.context['service']
        service_photo = ServicePhoto.objects.create(service=service, **validated_data)
        return service_photo

class ServiceSerializer(serializers.ModelSerializer):
    photos = ServicePhotoSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'refund_rate', 'upfront_rate', 'allow_points', 'photos']
    def validate(self, data):
        if len(data['photos']) < 2:
            raise serializers.ValidationError("At least two photos are required.")
        return data
    def create(self, validated_data):
        photos_data = validated_data.pop('photos')
        service = self.Meta.model.objects.create(**validated_data)

        for photo_data in photos_data:
            ServicePhotoSerializer(context={'service': service}).create(photo_data)

        return service
    def update(self, instance, validated_data):
        photos_data = validated_data.pop('photos', [])
        service = super().update(instance, validated_data)
        existing_photos = instance.photos.all()
        
        for photo in existing_photos:
            if photo.image not in [p['image'] for p in photos_data]:
                photo.delete()
                
        for photo_data in photos_data:
            photo = existing_photos.filter(image=photo_data['image']).first()
            if photo:
                ServicePhotoSerializer(photo, data=photo_data, context={'service': service}).update(photo, photo_data)
            else:
                ServicePhotoSerializer(context={'service': service}).create(photo_data)

        return service
    
class ServiceFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFavorite
        fields = ['id', 'service', 'created', 'modified']
        read_only_fields = ['created', 'modified']

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']

        # Check if the user has already favorited the service
        if ServiceFavorite.objects.filter(user=user, service=service).exists():
            raise serializers.ValidationError("You have already favorited this service.")

        service_favorite = ServiceFavorite.objects.create(user=user, **validated_data)
        return service_favorite

    def destroy(self, instance):
        user = self.context['request'].user
        if instance.user != user:
            raise serializers.ValidationError("You can only delete your own favorites.")
        instance.delete()
        return instance
    

    
class ServiceReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ServiceReview
        fields = ['id', 'rating', 'user', 'comment']
        read_only_fields = ['created_at', 'updated_at']
        
    
    
    

    