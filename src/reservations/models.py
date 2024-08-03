from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from djmoney.models.fields import MoneyField
import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.exceptions import ValidationError, SuspiciousOperation
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
import django.utils.timezone as timezone
from django.db import transaction
from decimal import Decimal, getcontext
from .exceptions import NonRefundableException, CantBeCanceled
import qrcode
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files.base import ContentFile

User = get_user_model()

# Create your models here.


class BaseReservation(models.Model):
    
    owner    = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE, editable=False)
    unpaid_amount = MoneyField(max_digits=14, decimal_places=2, default=Money(0.00, "USD"))
    scanned  = models.BooleanField(_("Scanned"), default=False)
    canceled = models.BooleanField(_("Canceled"), default=False)
    scan_date= models.DateTimeField(_("Ticket scan date time"), auto_now=False, auto_now_add=False, null=True, blank=True)
    uuid     = models.UUIDField(_("Unique Identifier"), default=uuid.uuid4, editable=False, unique=True)
    payments = GenericRelation('Payment', related_query_name='reservation')
    points_payments = GenericRelation('PointsPayment', related_query_name='reservation')
    refunds         = GenericRelation('Refund', related_query_name='reservation')
    qr_code         = models.ImageField(_("QR Code for uuid"), upload_to='reservations/qr_codes/', height_field=None, width_field=None, max_length=None)
    class Meta:
        abstract = True    
        
        
    def check_refundable(self):
        return (not self.canceled) and (not self.get_service().refund_rate.is_zero()) and (not self.scanned)
    
    def check_revocable(self):
        return (not self.canceled) and (not self.scanned)
    
    def check_scanable(self):
        return True
    
    def store_qr_code(self):
        if self.qr_code:
            return
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.uuid))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        file_name = f'qr_code_{self.uuid}.png'
        self.qr_code.save(file_name, ContentFile(buffer.read()), save=False)
        
    
    def clean(self) -> None:
        if not hasattr(self.owner, "creditcard"):
            raise ValidationError(_("User does not have payment information"))
        return super().clean()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None, use_points_discount=False, *args, **kwargs
    ):
        created = False
        if self.pk is None:
            created = True
            self.store_qr_code()
            
        self.full_clean()
                    
        self.subject = self.get_subject()
        self.service = self.get_service()
            
        subject = self.subject
        service = self.service
        full_price_obj = self.get_full_price()
        currency  = full_price_obj.currency
        full_price= full_price_obj.amount
        points_amount= subject.points_discount_price
        
        
        points_discount_amount = 0
        full_payment_amount = self.apply_discounts(full_price)
        if use_points_discount and service.allow_points:
                points_discount_amount = full_price * subject.points_discount_decimal
                full_payment_amount = full_price - points_discount_amount
        
        upfront_amount= service.upfront_rate_decimal * full_payment_amount
        unpaid_amount = full_payment_amount - upfront_amount
        self.unpaid_amount = Money(unpaid_amount, currency)
        
        upfront_amount = Decimal(upfront_amount).quantize(Decimal('0.00'))
        unpaid_amount  = Decimal(unpaid_amount).quantize(Decimal('0.00'))
        
        super().save(force_insert, force_update, using, update_fields)
        if created:
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
        return created
            
        
    
    def cancel(self):
        revocable = self.check_revocable()
        if not revocable:
            raise CantBeCanceled()
        self.canceled = True
        self.save()
    
    def refund(self):
        refundable = self.check_refundable()
        if not refundable:
            raise NonRefundableException()
        self.cancel()
        service = self.get_service()
        total_payments = self.payments.aggregate(total_sum=models.Sum('amount'))['total_sum'] * self.get_refund_rate()
        currency = self.payments.first().amount.currency
        if total_payments:
            Refund.objects.create(
                    content_object= self,
                    amount        = Money(total_payments.quantize(Decimal('0.00')), currency)
                )
        else:
            raise ValidationError(_("No payments found to refund."))
    def on_scan(self):
        self.scan_date = timezone.now()
        self.scanned = True
        self.save()
            
        
class TicketPurchase(BaseReservation):
    ticket   = models.ForeignKey("activities.Ticket", verbose_name=_("Ticket"), on_delete=models.CASCADE, related_name='purchases')
    qr_code  = models.ImageField(_("QR Code for uuid"), upload_to='reservations/tickets/qr_codes/')
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
        
    class Meta:
        ordering = ['-created']
        permissions = (
            ('scan_reservations', _('Can scan reservations')),
        )
        
    @property
    def refunded(self):
        return bool(self.refunds.count())
    
    @property
    def refundable(self):
        return self.check_refundable()
    
    @property
    def can_be_canceled(self):
        return self.check_revocable()
    
    def check_scanable(self):
        ticket_is_valid = self.ticket.is_valid
        ticket_activity_is_valid = True
        if hasattr(self.ticket.activity, "tour"):
            ticket_activity_is_valid = self.ticket.activity.tour.takeoff_date > timezone.now()
            ticket_activity_is_valid = ticket_activity_is_valid and not self.ticket.activity.canceled
        return bool(ticket_activity_is_valid and ticket_is_valid and self.can_be_canceled)
        
    def clean(self) -> None:
        self.validation_message = {}
        if not self.validate_ticket():
            raise ValidationError(self.validation_message)
        return super().clean()
    
    def clean_scan(self):
        if not self.check_scanable():
            raise ValidationError(_("Invalid Reservation."))
        
    
    def validate_ticket(self) -> bool:
        self.validation_message['ticket'] = []
        
        ticket_is_valid = self.ticket.is_valid
        if not ticket_is_valid:
            self.validation_message['ticket'].append(_("Ticket is expired"))
        
        ticket_activity_is_valid = True
        if hasattr(self.ticket.activity, "tour"):
            ticket_activity_is_valid = self.ticket.activity.tour.takeoff_date > timezone.now()
        ticket_activity_is_valid = ticket_activity_is_valid and not self.ticket.activity.canceled
            
        if not ticket_activity_is_valid:
            self.validation_message['activity']= _("Activity no longer available")
            
        ticket_stock_valid = self.ticket.stock >= 1
        if not ticket_stock_valid:
            self.validation_message['ticket'].append(_("Ticket is out of stock"))
            
        if not self.validation_message['ticket']:
            self.validation_message.pop('ticket')
        
        return bool(ticket_is_valid and ticket_activity_is_valid and ticket_stock_valid)
    
    def get_subject(self):
        return self.ticket
    
    def get_full_price(self):
        return self.ticket.price
    
    '''
    return a decimal between 0.0 and 1.0
    '''
    def get_refund_rate(self):
        if self.force_full_refund:
            return Decimal('1.0')
        else:
            return self.get_service().refund_rate_decimal
    
    def get_service(self):
        return self.ticket.activity
    
    def gift_user_points(self):
        if self.get_service().allow_points:
            self.owner.pointswallet.increase_point(0, self.get_service().points_gift)
    
    def apply_discounts(self, amount):
        return amount
    
    def check_refundable(self) -> bool:
        return (
            super().check_refundable() 
            or (((not self.canceled) and (not self.scanned)) and (self.ticket.canceled or self.ticket.activity.canceled))
            or (self.refundable_on_data_change())
        )
    def refundable_on_data_change(self) -> bool:
        return ((not self.canceled) and (not self.scanned)) and ((self.created < self.ticket.crucial_field_modified) or (self.created < self.ticket.activity.crucial_field_modified))
    @transaction.atomic()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None, use_points_discount=False
    ):
        
        created = super().save(force_insert, force_update, using, update_fields, use_points_discount)
        if created:
            self.ticket.stock -= 1
            self.ticket.save()

    @transaction.atomic()
    def cancel(self):
        self.ticket.stock += 1
        self.ticket.save()
        return super().cancel()
    
    @transaction.atomic()
    def refund(self):
        if self.refundable_on_data_change():
            self.force_full_refund = True
        return super().refund()
    
    
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
            raise ValidationError(_("Insufficient funds"))
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
    

class Refund(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id    = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    amount  = MoneyField(max_digits=14, decimal_places=2)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    def clean(self) -> None:
        if not hasattr(self.content_object.owner, "creditcard"):
            raise ValidationError(_("User does not have payment information"))
        return super().clean()
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        if self.pk is None:
            try:
                self.content_object.owner.creditcard.increase_balance(self.amount.amount, self.amount.currency)
            except ValueError as error:
                raise ValidationError(str(error))
        return super().save(force_insert, force_update, using, update_fields)