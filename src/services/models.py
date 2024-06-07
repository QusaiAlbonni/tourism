from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint

User = get_user_model()

class Service(models.Model):
    name = models.CharField(_("Name"), max_length=50)
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
    description = models.TextField(blank=True,verbose_name=_("Description"), null=True, max_length= 2048)
    refund_rate = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('95.0'))
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
    allow_points = models.BooleanField(null=False,default=False)
    allow_review = models.BooleanField(null=False,default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    def save(self, *args, **kwargs):
        # Call full_clean() to validate the model instance
        self.full_clean()
        super().save(*args, **kwargs)

class ServicePhoto(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='uploads/service_photos/')
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    def save(self, *args, **kwargs):
        # Check if the service already has 7 photos
        if self.service.photos.count() >= 7:
            raise ValidationError("Service can have at most 7 photos.")

        super().save(*args, **kwargs)

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
    comment = models.TextField(_("Review Comment"))
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

    def clean(self):
        if not self.service.allow_review:
            raise ValidationError(_("Reviews are not allowed for this service."))
        super().clean()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['service', 'user'], name='unique_service_review')
        ]
