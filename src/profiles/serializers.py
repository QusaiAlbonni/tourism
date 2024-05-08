from rest_framework import serializers
from address.models import Address
from .models import Profile

class ProfileAddressCreateSerializer(serializers.ModelSerializer):
    
    locality    = serializers.CharField(max_length=165, allow_blank=True, required=False)
    postal_code = serializers.CharField(max_length=10, allow_blank=True, required=False)
    state       = serializers.CharField(max_length=165, allow_blank=True, required=False)
    state_code  = serializers.CharField(max_length=8, allow_blank=True, required=False)
    country     = serializers.CharField(max_length=40, allow_blank=True, required=False)
    country_code= serializers.CharField(max_length=2, allow_blank=True, required=False)
    
    class Meta:
        model = Address
        fields = [
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
    def create(self, validated_data):
        user = self.context['request'].user
        profile = user.profile
        
        address = validated_data
        profile.address = address
        profile.save()
        address = profile.address
        
        return address
    def update(self, instance, validated_data):
        user = self.context['request'].user
        profile = user.profile
        
        address = validated_data
        profile.address = address
        profile.address.save()
        profile.save()
        address = profile.address
        
        return address
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'marital_status', 'birth_date', 'num_kids', 'avatar']
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    def update(self, instance, validated_data):
        instance = self.context['request'].user.profile
        return super().update(instance, validated_data)
        