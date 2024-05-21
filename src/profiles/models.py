from django.db import models
from datetime import  timedelta
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend
from django.core.validators import MaxValueValidator, MinValueValidator
from address.models import AddressField
from app_media.models import AvatarField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE, editable= False)
    
    bio            = models.TextField(blank=True,verbose_name=_("Bio"), null=True, max_length= 2048)
    marital_status = models.BooleanField(default=False, verbose_name=_("Marital Status"))
    birth_date     = models.DateField(blank=True, null=True,auto_now=False, auto_now_add=False, verbose_name=_("Birth Date"))
    num_kids       = models.IntegerField(default= 0, verbose_name=_("Number of Children"), validators=[MaxValueValidator(30), MinValueValidator(0)])
    
    avatar  = AvatarField(_("Avatar"), upload_to="uploads/profiles/avatars", max_length=1024,max_size= (256,256), null=True)
    
    address = AddressField(related_name='+', blank=True, null=True)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    required_fields = ['user']
    
    def __str__(self) -> str:
        return super().__str__()

class CreditCard(models.Model):
    CARD_TYPES = (
        ('Visa', 'Visa'),
        ('Mastercard', 'Mastercard'),
        ('American Express', 'American Express'),     
    )
    card_number = models.CharField(max_length=16, unique=True)
    holder_name = models.CharField(max_length=100)
    expiration_date = models.DateField()
    ccv = models.CharField(max_length=4)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='USD',default=5000)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)

    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE, editable= False)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

    def decrease_balance(self, amount, currency):
        OpenExchangeRatesBackend().update_rates()
        converted_amount = convert_money(Money(amount, currency),self.balance.currency)
        self.balance -= converted_amount
        self.save()
    
class PointsWallet(models.Model):

    num_points = models.IntegerField(default=10)

    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE, editable= False)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False) 

    @property
    def expiration_date(self):
        return self.modified + timedelta(days=90)  
    
    def increase_point(self,pay,extra_point=0):
        #extra point to backage
        amount=pay*0.0
        self.num_points+=(amount+extra_point)
        self.save()

    def decrease_point(self,amount):
        if amount>self.num_points:
            raise ValueError("Insufficient points")
        self.num_points-=amount
        self.save()
    # user should have at lest three reserv to can pay by point
    def user_can(self):
        ...

class Favorite(models.Model):
    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE, editable= False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False) 
    
    @classmethod
    def add_favorite(cls, user, obj):
        content_type = ContentType.objects.get_for_model(obj)
        cls.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=obj.id
        )

    @classmethod
    def remove_favorite(cls, user, obj):
        content_type = ContentType.objects.get_for_model(obj)
        cls.objects.filter(
            user=user,
            content_type=content_type,
            object_id=obj.id
        ).delete()

    @classmethod
    def get_favorites(cls, user, model=None):
        if model:
            content_type = ContentType.objects.get_for_model(model)
            return cls.objects.filter(user=user, content_type=content_type)
        return cls.objects.filter(user=user)