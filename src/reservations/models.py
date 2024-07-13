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
from django.core.exceptions import ValidationError, SuspiciousOperation
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
import django.utils.timezone as timezone
from django.db import transaction
from decimal import Decimal, getcontext

User = get_user_model()

# Create your models here.


class BaseReservation(models.Model):
    
    owner    = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE, editable=False)
    unpaid_amount = MoneyField(max_digits=14, decimal_places=2, default=Money(0.00, "USD"))
    scanned  = models.BooleanField(_("Scanned"), default=False)
    canceled = models.BooleanField(_("Canceled"), default=False)
    scan_date= models.DateTimeField(_("Ticket scan date time"), auto_now=False, auto_now_add=False, null=True, blank=True)
    uuid     = models.UUIDField(_("Unique Identifier"), default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        abstract = True    
    def clean(self) -> None:
        if not hasattr(self.owner, "creditcard"):
            raise ValidationError(_("User does not have payment information"))
        return super().clean()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None, use_points_discount=False, *args, **kwargs
    ):
        if self.pk is None:
            self.created = True
                    
        self.subject = self.get_subject()
        self.service = self.get_service()
            
        subject = self.subject
        service = self.service
        currency  = self.get_full_price().currency
        full_price= self.get_full_price().amount
        points_amount= subject.points_discount_price
        print(use_points_discount)
        
        points_discount_amount = 0
        full_payment_amount = full_price
        if use_points_discount and service.allow_points:
                points_discount_amount = full_price * subject.points_discount_decimal
                full_payment_amount = full_price - points_discount_amount
        
        upfront_amount= service.upfront_rate_decimal * full_payment_amount
        unpaid_amount = full_payment_amount - upfront_amount
        self.unpaid_amount = Money(unpaid_amount, currency)
        
        upfront_amount = Decimal(upfront_amount).quantize(Decimal('0.00'))
        unpaid_amount  = Decimal(unpaid_amount).quantize(Decimal('0.00'))
        
        instance = super().save(force_insert, force_update, using, update_fields)
        if self.created:
            if not upfront_amount and not points_discount_amount:
                raise SuspiciousOperation(_("Impossible situation encountered."))
            if upfront_amount:
                Payment.objects.create(
                    content_object= self,
                    discount      = Decimal(1.0) - upfront_amount / full_price,
                    amount        = Money(upfront_amount, currency)
                )
            if points_discount_amount:
                PointsPayment.objects.create(
                    content_object= self,
                    amount        = points_amount
                )
        self.gift_user_points()
        

class TicketPurchase(BaseReservation):
    ticket   = models.ForeignKey("activities.Ticket", verbose_name=_("Ticket"), on_delete=models.CASCADE)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    class Meta:
        ordering = ['-created']
    
    def clean(self) -> None:
        self.validation_message = {}
        if not self.validate_ticket():
            raise ValidationError(self.validation_message)
        return super().clean()
    
    def validate_ticket(self) -> bool:
        self.validation_message['ticket'] = []
        
        ticket_is_valid = self.ticket.is_valid
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
    
    def get_subject(self):
        return self.ticket
    
    def get_full_price(self):
        return self.ticket.price
    
    def get_service(self):
        return self.ticket.activity
    
    def gift_user_points(self):
        if self.get_service().allow_points:
            self.owner.pointswallet.increase_point(0, self.get_service().points_gift)
    
    @transaction.atomic()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None, use_points_discount=False
    ):
        self.full_clean()
        if self.pk is None:
            self.ticket.stock -= 1
            self.ticket.save()
            
            self.scan_date = None
        return super().save(force_insert, force_update, using, update_fields, use_points_discount)
    
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
        converted_amount = convert_money(Money(self.amount.amount, self.amount.currency),self.content_object.owner.creditcard.balance.currency)
        if converted_amount > self.content_object.owner.creditcard.balance:
            raise ValidationError("Insufficient funds")
        return super().clean()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        if self.pk is None:
            try:
                self.content_object.owner.creditcard.decrease_balance(self.amount.amount, self.amount.currency)
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
            raise ValidationError(_("Insufficient points funds"))
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
    
