from rest_framework import serializers
from .models import Property, SupProperty, SupPropertyBed, SupPropertyPhoto, PropertyTag, SupPropertyTag
from address.models import Address
from services.serializers import ServiceSerializer
from django.http import JsonResponse
from django.core.exceptions import ValidationError

class AddressSerializer(serializers.ModelSerializer):
    locality     = serializers.CharField(max_length=165, allow_blank=True, required=False)
    postal_code  = serializers.CharField(max_length=10, allow_blank=True, required=False)
    state        = serializers.CharField(max_length=165, allow_blank=True, required=False)
    state_code   = serializers.CharField(max_length=8, allow_blank=True, required=False)
    country      = serializers.CharField(max_length=40, allow_blank=True, required=False)
    country_code = serializers.CharField(max_length=2, allow_blank=True, required=False)
    
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

class SupPropertyBedSerializer(serializers.ModelSerializer):
    supproperty = serializers.PrimaryKeyRelatedField(
        queryset=SupProperty.objects.all(),
        required=False
    )
    capacity = serializers.ReadOnlyField()
    class Meta:
        model = SupPropertyBed
        fields = [
            'id',
            'supproperty',
            'type',
            'number',
            'capacity',
            'created',
            'modified'
        ]
        read_only_fields = ['id','capacity','supproperty','created','modified']
    def create(self, validated_data):
        supproperty = validated_data.pop('supproperty')
        supproperty_bed = self.Meta.model.objects.create(supproperty=supproperty, **validated_data)
        return supproperty_bed
    def update(self, instance, validated_data):
        supproperty = instance.supproperty
        supproperty_type = supproperty.type
        bed_types = [validated_data.get('type', instance.type)]
        bed_types.extend(
            supproperty.beds.exclude(id=instance.id).values_list('type', flat=True)
        )

        if supproperty_type == 'Suite' and 'King' not in bed_types:
            raise serializers.ValidationError("A Suite must have at least one King bed.")
        if supproperty_type == 'Family':
            if not any(bed in bed_types for bed in ['Single', 'Double', 'King']):
                raise serializers.ValidationError("A Family room must have at least one of Single, Double, or King bed.")
            if not any(bed in bed_types for bed in ['Cheldren', 'DoubleCheldren']):
                raise serializers.ValidationError("A Family room must have at least one of Cheldren or DoubleCheldren bed.")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
            
class SupPropertyPhotoSerializer(serializers.ModelSerializer):
    supproperty = serializers.PrimaryKeyRelatedField(
        queryset=SupProperty.objects.all(),
        write_only=True,
        required=False
    )
    class Meta:
        model = SupPropertyPhoto
        fields = '__all__'

    def create(self, validated_data):
        supproperty = validated_data.pop('supproperty')
        try:
            supproperty_photo = SupPropertyPhoto.objects.create(supproperty=supproperty, **validated_data)
        except ValidationError as e:
            raise serializers.ValidationError({'detail': str(e)})
        return supproperty_photo

class SupPropertySerializer(serializers.ModelSerializer):
    adults_capacity = serializers.ReadOnlyField()
    children_capacity = serializers.ReadOnlyField()
    points_discount_decimal = serializers.ReadOnlyField()
    beds = SupPropertyBedSerializer(many=True,required=False)
    photos = SupPropertyPhotoSerializer(many=True,required=False)
    property_id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = SupProperty
        fields = [
            'id',
            'property_id',
            'type',
            'name',
            'description',
            'number',
            'price',
            'multi_night_discount',
            'available_start_date',
            'available_end_date',
            'points_discount_price',
            'points_discount',
            'points_discount_decimal',
            'adults_capacity',
            'children_capacity',
            'created',
            'modified',
            'beds',
            'photos'
        ]
    read_only_fields = ['id','created','modified','points_discount_decimal','children_capacity','adults_capacity']
    
    def create(self, validated_data):
        beds_data = validated_data.pop('beds',[])
        photos_data = validated_data.pop('photos', [])

        if len(photos_data) < 2:
            raise serializers.ValidationError("At least two photos are required.")
        if len(beds_data) < 1:
            raise serializers.ValidationError("At least one bed is required.")
        
        sup_property_type = validated_data.get('type')
        self.validate_beds_for_type(sup_property_type, beds_data)

        supProperty = self.Meta.model.objects.create(**validated_data)

        for photo_data in photos_data:
            photo_data['supproperty'] = supProperty
            SupPropertyPhotoSerializer(data=photo_data).create(photo_data)

        for bed_data in beds_data :
            bed_data['supproperty'] = supProperty
            SupPropertyBedSerializer(data=bed_data).create(bed_data)
        return supProperty
    
    def update(self, instance, validated_data):
        beds_data = validated_data.pop('beds', [])
        sup_property_type = validated_data.get('type', instance.type)
        self.validate_beds_for_type(sup_property_type, beds_data)
        if len(beds_data) < 1:
            raise serializers.ValidationError("At least one bed is required.")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.beds.all().delete()
        for bed_data in beds_data :
            bed_data['supproperty'] = instance
            SupPropertyBedSerializer(data=bed_data).create(bed_data)
        return instance

    def validate_beds_for_type(self, property_type, beds_data):
        bed_types = [bed['type'] for bed in beds_data]
        
        if property_type == 'Suite':
            if 'King' not in bed_types:
                raise serializers.ValidationError("A Suite must have at least one King bed.")
        elif property_type == 'Family':
            if not any(bed in bed_types for bed in ['Single', 'Double', 'King']):
                raise serializers.ValidationError("A Family room must have at least one of Single, Double, or King bed.")
            if not any(bed in bed_types for bed in ['Cheldren', 'DoubleCheldren']):
                raise serializers.ValidationError("A Family room must have at least one of Cheldren or DoubleCheldren bed.")   

class PropertySerializer(ServiceSerializer):
    address = AddressSerializer(required=True, allow_null= False)

    class Meta:
        model = Property
        fields =ServiceSerializer.Meta.fields +  [
            'id',
            'name',
            'description',
            'address',
            'star',
            'type',
            'desgen'
        ]
        read_only_fields = [
            'id'
        ]
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        service_instance = super(PropertySerializer, self).update(instance, validated_data)
        if address_data:
            AddressSerializer().update(instance.address, address_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class PropertyTagSerializer(serializers.ModelSerializer):
    # property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = PropertyTag
        fields = '__all__'

class SupPropertyTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupPropertyTag
        fields = '__all__'