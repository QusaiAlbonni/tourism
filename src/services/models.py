from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint
from django.db.models import Avg
from profanity.validators import validate_is_profane
from events.models import Event
from django.db.models import Sum
from django.db.models import Q

User = get_user_model()

class Service(models.Model):
    name = models.CharField(_("Name"), max_length=50,unique=False)
    description = models.TextField(blank=True,verbose_name=_("Description"), null=True, max_length= 2048)
    favorited_by = models.ManyToManyField(
        User,
        verbose_name= "Favorited by Users",
        through="ServiceFavorite",
        through_fields=("service", "user"),
        related_name="favorited_services"
        )
    review_by = models.ManyToManyField(
        User,
        verbose_name= "Review by Users",
        through="ServiceReview",
        through_fields=("service", "user"),
        related_name="reviewed_services"
        )
    refund_rate = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('100.0'))
        ]
    )
    upfront_rate = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('100.0'))
        ]
    )
    allow_points = models.BooleanField(null=False,default=True)
    allow_review = models.BooleanField(null=False,default=True)
    points_gift = models.PositiveIntegerField(_("Gifted points"),
                                            validators=[MaxValueValidator(10000), MinValueValidator(1)]
                                        )
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    @property
    def avg_rating(self):
        return self.servicereview_set.aggregate(Avg('rating'))['rating__avg']
    @property
    def num_rating(self):
        return self.servicereview_set.count()
    @property
    def discount(self):
        discounts = ServiceDiscount.objects.filter(
        Q(service=self) & Q(event__isnull=True) |
        Q(service=self) & Q(event__activate=True) |
        Q(service__isnull=True)
        )

        total_discount = 1
        for discount in discounts:
            total_discount *= (Decimal(1) - discount.percent / Decimal(100))

        return Decimal((1 - total_discount)*100).quantize(Decimal('0.00'))

    
    @property
    def on_discount(self):
        discounts = ServiceDiscount.objects.filter(
            Q(service=self) & Q(event__isnull=True) |
            Q(service=self) & Q(event__activate=True) |
            Q(service__isnull=True)
        )
        return [self.discount_to_dict(discount) for discount in discounts]

    def discount_to_dict(self, discount):
        return {
            "id": discount.id,
            "percent": str(discount.percent),  # Convert Decimal to string for JSON serialization
            "event": discount.event.name if discount.event else None,
            "type": discount.type,
        }
    @property
    def upfront_rate_decimal(self):
        return self.upfront_rate / Decimal(100)
    @property
    def refund_rate_decimal(self):
        return self.refund_rate / Decimal(100)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class ServicePhoto(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='uploads/service_photos/')
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    def save(self, *args, **kwargs):
        if self.service.photos.count() >= 7:
            raise ValidationError("Service can have at most 7 photos.")
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        if self.service.photos.count() <= 2:
            raise ValidationError("A service must have at least two photos.")
        super().delete(*args, **kwargs)
    
class ServiceFavorite(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

class ServiceReview(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True
    )
    comment = models.TextField(_("Review Comment"),validators=[validate_is_profane], max_length= 1024)

    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

    def save(self, *args, **kwargs):
        if not self.service.allow_review:
            raise ValidationError(_("Reviews are not allowed for this service."))
        super().save(*args, **kwargs)
    class Meta:
        constraints = [
            UniqueConstraint(fields=['service', 'user'], name='unique_service_review')
        ]

class ServiceDiscount(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True,blank=True, related_name='discounts')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True,blank=True, related_name='events')

    percent = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('79.0'))
        ]
    )
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

    @property
    def type(self):
        service=None
        event=None
        if self.service is None:
            service='all'
        else:
            service='specific'
        if self.event is None:
            event='null'
        else:
            event='specific'
        return F'{service} service ,{event} event'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'event'],
                name='unique_service_event'
            ),
            models.UniqueConstraint(
                fields=['service'],
                condition=models.Q(event__isnull=True),
                name='unique_service_null_event'
            ),
            models.UniqueConstraint(
                fields=['event'],
                condition=models.Q(service__isnull=True),
                name='unique_service_event_sd'
            )
        ]
    
    def clean(self):
        if self.service is None and self.event is None:
            if ServiceDiscount.objects.filter(service__isnull=True, event__isnull=True).exists():
                raise ValidationError("A discount with both service and event set to null already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)