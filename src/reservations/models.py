from typing import Iterable, Optional
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from djmoney.models.fields import MoneyField
import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import datetime
from django.core.exceptions import ValidationError
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
import django.utils.timezone as timezone

User = get_user_model()

# Create your models here.


class BaseReservation(models.Model):
    class Meta:
        abstract = True    

class TicketPurchase(BaseReservation):
    ticket   = models.ForeignKey("activities.Ticket", verbose_name=_("Ticket"), on_delete=models.CASCADE)
    owner    = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE, editable=False)
    scanned  = models.BooleanField(_("Scanned"), default=False)
    canceled = models.BooleanField(_("Canceled"), default=False)
    scan_date= models.DateTimeField(_("Ticket scan date time"), auto_now=False, auto_now_add=False, null=True, blank=True)
    uuid     = models.UUIDField(_("Unique Identifier"), default=uuid.uuid4, editable=False, unique=True)
    canceled = models.BooleanField(_(""), default=False)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    def clean(self) -> None:
        self.validation_message = {}
        if not self.validate_ticket():
            raise ValidationError(self.validation_message)
        return super().clean()
    
    def validate_ticket(self) -> bool:
        self.validation_message['ticket'] = []
        
        ticket_is_valid = self.ticket.valid_until > datetime.datetime.now().date()
        if not ticket_is_valid:
            self.validation_message['ticket'].append("Ticket is expired")
        
        ticket_activity_is_valid = True
        if hasattr(self.ticket.activity, "tour"):
            ticket_activity_is_valid = self.ticket.activity.tour.takeoff_date > timezone.now()
            
        if not ticket_activity_is_valid:
            self.validation_message['activity']= "Activity no longer available"
            
        ticket_stock_valid = self.ticket.stock >= 1
        if not ticket_stock_valid:
            self.validation_message['ticket'].append("Ticket is out of stock")
        
        return bool(ticket_is_valid and ticket_activity_is_valid and ticket_stock_valid)
    
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        if self.pk is None:
            self.ticket.stock -= 1
            self.ticket.save()
            
            self.scan_date = None
        return super().save(force_insert, force_update, using, update_fields)
    
class Payment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id    = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    amount  = MoneyField(max_digits=14, decimal_places=2)
    discount= models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    def clean(self) -> None:
        if not hasattr(self.content_object.owner, "creditcard"):
            raise ValidationError(_("User does not have payment information"))
        converted_amount = convert_money(Money(self.amount, self.amount.currency),self.content_object.owner.creditcard.balance.currency)
        if converted_amount > self.content_object.owner.creditcard.balance:
            raise ValidationError("Insufficient funds")
        return super().clean()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        if self.pk is None:
            try:
                self.content_object.owner.creditcard.decrease_balance(self.amount, self.amount.currency)
            except ValueError as error:
                raise ValidationError(str(error))
        return super().save(force_insert, force_update, using, update_fields)
    
class PointsPayment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    amount  = models.PositiveIntegerField(_("Points Amount"))
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    def clean(self) -> None:
        if self.amount > self.content_object.owner.pointswallet.num_points:
            raise ValidationError("Insufficient funds")
        return super().clean()
    
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        if self.pk is None:
            try:
                self.content_object.owner.pointswallet.decrease_point(self.amount)
            except ValueError as error:
                raise ValidationError(str(error))
        return super().save(force_insert, force_update, using, update_fields)