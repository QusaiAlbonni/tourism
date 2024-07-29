import datetime
from datetime import datetime as dt
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from app_media.models import AvatarField
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import timedelta, now
from tags.models import Tag
from djmoney.models.validators import MinMoneyValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from address.models import AddressField
from services.models import Service
from .validators import DateLessThanToday
from django.core.exceptions import ValidationError
from reservations.models import TicketPurchase
from reservations.services import refund_all_purchases
User = get_user_model()
from tags.models import SupTag



class Guide(models.Model):
    
    name  = models.CharField(_("Name"), max_length=150, unique=True)
    bio   = models.TextField(_("Guide's Bio"), max_length=2048, blank=True, null=True)
    avatar= AvatarField(_("Avatar"), upload_to="uploads/guides/avatars" , null=True, max_length=1024, max_size=(128, 128))
    email = models.EmailField(_("Email"), blank=True, null=True)
    
    #country = models.ForeignKey(Country, verbose_name=_("Country Of origins"), on_delete=models.SET_NULL, blank=True, null=True)
    
    #available = models.BooleanField(_("Availability"), default=True)
    
    likers = models.ManyToManyField(
        User,
        verbose_name=_("Likers"),
        through= "GuideLiker",
        through_fields=("guide","user"),
        related_name='liked_guides'
    )
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    
    popularity_period = now() - timedelta(days=30)
    top_num = 10
    
    class Meta:
        ordering = ["-created"]

        
    
    @property
    def likes(self):
        return self.likers.count()
    @property
    def is_popular(self):
        popular_guides =Guide.objects.annotate(
            popularity=models.Count(
                "likers",
                filter=models.Q(guideliker__modified__gte=self.popularity_period)
                )
            ).order_by("-popularity")[:self.top_num]
        if self.likers.count() == 0:
            return False
        return bool(self in popular_guides)
        
    
    def toggle_like(self, user : AbstractUser) -> bool:
        if user is None:
            raise User.DoesNotExist
        if self.likers.filter(pk=user.pk).exists():
            self.likers.remove(user)
            return False
        else:
            self.likers.add(user)
            return True
        
    def is_liked_by_user(self, user : AbstractUser) -> bool:
        return self.likers.filter(pk=user.pk).exists()


class GuideLiker(models.Model):
    guide   = models.ForeignKey(Guide, on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    
class Activity(Service):
    canceled = models.BooleanField(_("Canceled"), default=False)
    tags    = models.ManyToManyField(
        Tag,
        verbose_name=_("Tags"),
        through="ActivityTag",
        through_fields=("activity", "tag")
        )
    crucial_field_modified = models.DateTimeField(auto_now=False, auto_now_add=True)
    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
    @property
    def type(self):
        return self.get_type()
    
    def get_type(self):
        if hasattr(self, "tour"):
            return "tour"
        else:
            return "listing"
    def refund_all(self):
        queryset = TicketPurchase.objects.filter(ticket__activity = self, canceled= False, scanned= False)
        
        refund_all_purchases(queryset, TicketPurchase)
    
    
class Tour(Activity):
    takeoff_date = models.DateTimeField(_("Takeoff date"), auto_now=False, auto_now_add=False, validators=[DateLessThanToday(1)])
    duration     = models.DurationField(_("Tour Duration"))
    guide        = models.ForeignKey(Guide, verbose_name=_("Guide"), on_delete=models.SET_NULL, null=True)
    sites        = models.ManyToManyField(
        "Site",
        through="TourSite",
        verbose_name=_("Sites"),
        through_fields=("tour","site"),
        related_name='tours'
    )
    
    @property
    def end_date(self)-> datetime.datetime:
        return self.takeoff_date + self.duration
    def clean(self) -> None:
        takeoff_date = self.takeoff_date
        end_date     = self.end_date
        if Tour.objects.annotate(
            end_date=models.ExpressionWrapper(models.F('takeoff_date') + models.F('duration'), output_field=models.DateTimeField())
            ).filter(
            models.Q(guide=self.guide)&
            models.Q(takeoff_date__lt=end_date) &
            models.Q(end_date__gt=takeoff_date)
        ).exists():
            raise ValidationError(_("this guide is not available at the selected time period"))
        return super().clean()
    
    def takeoff_date_before_now(self):
        return self.takeoff_date < now()
    class Meta:
        ordering = ['-modified']
    
    class SensitiveMeta:
        # sensitive fields critical to the business
        critical_fields = (
            'duration',
            'takeoff_date'
        )
        critical_update_datefield = 'crucial_field_modified'
    

class Listing(Activity):
    opens_at   = models.TimeField(_("Opens At Time"), auto_now=False, auto_now_add=False)
    work_hours = models.DecimalField(max_digits=4, decimal_places=2, validators=[MaxValueValidator(23.99)])
    site       = models.ForeignKey('Site', verbose_name=_("Site"), on_delete=models.CASCADE, related_name='listings')
    website    = models.URLField(_("Link"), max_length=200, null=True, blank=True)
    @property
    def closes_at(self) -> datetime.time:
        opening_datetime = dt.combine(dt.today(), self.opens_at)
        closing_datetime = opening_datetime + timedelta(hours=float(self.work_hours))
        return closing_datetime.time()
    def clean(self) -> None:
        opens_at_datetime = datetime.datetime.combine(datetime.datetime.today(), self.opens_at)

        work_hours_int = int(self.work_hours)
        work_minutes = (self.work_hours - work_hours_int) * 60

        closing_time = opens_at_datetime + timedelta(hours=work_hours_int, minutes=float(work_minutes))

        if closing_time.time() < self.opens_at:
            raise ValidationError("The sum of opens_at and work_hours exceeds 24 hours.")
        return super().clean()
    class Meta:
        ordering = ['-modified']
    
    class SensitiveMeta:
        # sensitive fields critical to the business
        critical_fields = (
            'site',
        )
        critical_update_datefield = 'crucial_field_modified'
        
    

class Ticket(models.Model):
    activity= models.ForeignKey(Activity, verbose_name=_("Activity"), on_delete=models.CASCADE, related_name='tickets')
    name    = models.CharField(_("Name of the ticket"), max_length=50, null=False, blank=False)
    description = models.TextField(_("Description"), null=True, blank=True)
    price       = MoneyField(max_digits=14,
                        decimal_places=2,
                        default_currency='USD',
                        validators=[
                            MinMoneyValidator(Decimal('0.01')),
                        ])
    points_discount_price= models.IntegerField(validators=[MinValueValidator(int('1'))])
    points_discount      = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('100.0'))
        ]
    )
    stock       = models.PositiveIntegerField(_("Stock"), validators=[MaxValueValidator(int(1e6)), MinValueValidator(int(1))], default=100)
    valid_until = models.DateField(validators=[DateLessThanToday(1,inclusive=True)])
    canceled = models.BooleanField(_("Canceled"), default=False)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    crucial_field_modified = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    class Meta:
        ordering = ['-modified']
    class SensitiveMeta:
        # sensitive fields critical to the business
        critical_fields = (
            'valid_until',
        )
        critical_update_datefield = 'crucial_field_modified'
    
    @property
    def is_valid(self)-> bool:
        acitvity_valid = True
        if hasattr(self.activity, "tour"):
            acitvity_valid = self.valid_until <= self.activity.tour.takeoff_date.date()
        return bool((self.valid_until > datetime.datetime.now().date()) and acitvity_valid and not self.canceled)
    
    @property
    def points_discount_decimal(self):
        return self.points_discount / Decimal(100)
    
    def get_activity_type(self):
        return self.activity.get_type()
   
        
    def refund_all(self):
        queryset = TicketPurchase.objects.filter(canceled= False, scanned= False, ticket = self)
        refund_all_purchases(queryset= queryset, model=TicketPurchase)
    
class ActivityTag(SupTag):
    activity= models.ForeignKey(Activity, verbose_name=_("Activity"), on_delete=models.CASCADE, related_name='activity_tags')
    allowed_category_type = 'Activity'
    
class TourSite(models.Model):
    tour = models.ForeignKey("Tour", verbose_name=_("Tour"), on_delete=models.CASCADE, related_name='tour_sites')
    site = models.ForeignKey("Site", verbose_name=_("Site"), on_delete=models.CASCADE, related_name='site_tours')
    order= models.PositiveIntegerField(_("Order"))
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tour', 'order'], name='unique_tour_order'),
            models.UniqueConstraint(fields=['tour', 'site'], name='unique_tour_site')
        ]
        ordering = ['order']
    class SensitiveMeta:
        # sensitive fields critical to the business
        critical_fields = (
            'order',
            'site'
        )
        critical_update_datefield = 'tour.crucial_field_modified'
        date_field_model = 'tour'

    
class Site(models.Model):
    photo   = AvatarField(_("Photo"), max_size=(1024, 1024),upload_to="uploads/sites")
    address = AddressField(null=True)
    name    = models.CharField(_("Name"), max_length=50)
    description= models.TextField(_("Description"), null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    class Meta:
        ordering = ['name']
        