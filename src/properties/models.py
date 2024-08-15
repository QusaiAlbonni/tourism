from django.db import models
from services.models import Service
from tags.models import SupTag
from djmoney.models.fields import MoneyField
from address.models import AddressField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from djmoney.models.validators import MinMoneyValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

class Property(Service):
    PROPERTY_TYPE=[
       ('Hotel','Hotel'),
       ('Apartment','Apartment'),
       ('Chalet','Chalet')
    ]
    PROPERTY_DESGEN=[
       ('Modern','Modern'),
       ('Old','Old'),
    ]
    type = models.CharField(max_length=30,choices=PROPERTY_TYPE)
    desgen = models.CharField(max_length=20,choices=PROPERTY_DESGEN)
    star = models.PositiveSmallIntegerField(
        verbose_name="Star",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    address = AddressField(null=True)

class SupProperty(models.Model):
    SUP_PROPERTY_TYPE=[
       ('Standard','Standard'),
       ('Deluxe','Deluxe'),
       ('Suite','Suite'),
       ('Family','Family'),
    ]
    property_id = models.ForeignKey(Property,on_delete=models.CASCADE,related_name='supproperties')
    type = models.CharField(max_length=30,choices=SUP_PROPERTY_TYPE)    
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True,verbose_name=_("Description"), null=True, max_length= 2048)   
    number= models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50)
        ])

    price = MoneyField(max_digits=14,
                        decimal_places=2,
                        default_currency='USD',
                        validators=[
                            MinMoneyValidator(0),
                        ])
    multi_night_discount =models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('40.0'))
        ],
        default = 0.0
    )

    available_start_date = models.DateField() 
    available_end_date = models.DateField() 
    points_discount_price= models.IntegerField(validators=[MinValueValidator(int('1'))])
    points_discount      = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('100.0'))
        ]
    )   
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

    @property
    def adults_capacity(self):
        return sum(bed.capacity for bed in self.beds.filter(type__in=['Single', 'Double', 'King']))     

    @property
    def children_capacity(self):
        return sum(bed.capacity for bed in self.beds.filter(type__in=['Cheldren', 'DoubleCheldren']))

    @property
    def points_discount_decimal(self):
        return self.points_discount / Decimal(100)  
    
    def clean(self):
        if self.available_end_date and self.available_start_date and self.available_end_date < self.available_start_date:
            raise ValidationError("The available end date must be greater than the available start date.")  

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class SupPropertyBed(models.Model):
    BED_TYPE=[
        ('Single','Single'),
        ('Double',"Double"),
        ('King','King'),
        ('Cheldren','Cheldren'),
        ('DoubleCheldren','DoubleCheldren'),
    ]
    supproperty = models.ForeignKey(SupProperty,on_delete=models.CASCADE,related_name='beds')
    type = models.CharField(max_length=20,choices=BED_TYPE)

    number = models.SmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(3)
        ])
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

    @property
    def capacity(self):
        if self.type in ['Single', 'Children']:
            return self.number  
        else:
            return self.number * 2
        
    def delete(self, *args, **kwargs):
        if self.supproperty.photos.count() <= 1:
            raise ValidationError("A room must have at least one bed.")
        super().delete(*args, **kwargs)

class SupPropertyPhoto(models.Model):
    supproperty = models.ForeignKey(SupProperty,on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='uploads/service_photos/room_photos/')
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    def save(self, *args, **kwargs):
        if self.supproperty.photos.count() >= 3:
            raise ValidationError("A room can have at most 3 photos.")
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        if self.supproperty.photos.count() <= 2:
            raise ValidationError("A room must have at least two photos.")
        super().delete(*args, **kwargs)

class PropertyTag(SupTag):
    property = models.ForeignKey(Property,verbose_name=_("Property"),on_delete=models.CASCADE,related_name='property_tags')
    allowed_category_type = 'Property'
    class Meta:
        unique_together = ('tag', 'property')

class SupPropertyTag(SupTag):
    supproperty = models.ForeignKey(SupProperty,on_delete=models.CASCADE)
    allowed_category_type = 'SupProperty'
    class Meta:
        unique_together = ('tag', 'supproperty')
