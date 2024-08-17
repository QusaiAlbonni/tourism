from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import CreditCard,PointsWallet
from django.core.validators import MinLengthValidator
from datetime import  timedelta
from address.models import Address
from .models import Profile
from djmoney.contrib.exchange.models import Rate
from decimal import Decimal

User = get_user_model()


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        exclude = ('created', 'modified','id','user')
        read_only_fields = ('is_expired',)
    # we need it for check and notification 
    def get_is_expired(self, obj):
        return obj.expiration_date < timezone.now().date()
    # we need it for check when pay
    def get_balance(self,obj):
        return obj.balance
    def validate_ccv(self, value):
        validators = [MinLengthValidator(4)]
        for validator in validators:
            validator(value)
        return value
    def create(self, validated_data):
        validated_data['balance'] = Decimal('5000')
        return super().create(validated_data)

    
    
class PointsWalletSerializer(serializers.ModelSerializer):
    expiration_date = serializers.SerializerMethodField()

    class Meta:
        model = PointsWallet
        fields = ['num_points', 'expiration_date']

    def get_expiration_date(self, obj):
        return obj.modified + timedelta(days=90)

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
            'formatted',
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
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'marital_status', 'birth_date', 'num_kids', 'avatar', 'full_name']
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    def update(self, instance, validated_data):
        instance = self.context['request'].user.profile
        return super().update(instance, validated_data)
    def get_full_name(self, obj):
        return obj.user.get_full_name()

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ('id', 'currency', 'value')
        
    
