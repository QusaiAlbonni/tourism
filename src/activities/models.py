import datetime
from datetime import datetime as dt
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from app_media.models import AvatarField
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import AbstractUser
from address.models import Country
from django.utils.timezone import timedelta, now
from tags.models import Tag
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from address.models import AddressField
from services.models import Service
from .validators import DateLessThanToday
User = get_user_model()



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
    tags    = models.ManyToManyField(
        Tag,
        verbose_name=_("Tags"),
        through="ActivityTag",
        through_fields=("activity", "tag")
        )
    
class Tour(Activity):
    takeoff_date = models.DateTimeField(_(""), auto_now=False, auto_now_add=False, validators=[DateLessThanToday(now())])
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
    def end_date(self):
        return self.takeoff_date + self.duration
    

class Listing(Activity):
    opens_at   = models.TimeField(_(""), auto_now=False, auto_now_add=False)
    work_hours = models.DecimalField(max_digits=4, decimal_places=2)
    site       = models.ForeignKey('Site', verbose_name=_(""), on_delete=models.CASCADE, related_name='listings')
    website    = models.URLField(_("Link"), max_length=200, null=True, blank=True)
    @property
    def closes_at(self):
        opening_datetime = dt.combine(dt.today(), self.opens_at)
        closing_datetime = opening_datetime + timedelta(hours=float(self.work_hours))
        return closing_datetime.time()
    

class Ticket(models.Model):
    activity= models.ForeignKey(Activity, verbose_name=_("Activity"), on_delete=models.CASCADE, related_name='tickets')
    name    = models.CharField(_("Name of the ticket"), max_length=50, null=False, blank=False)
    description = models.TextField(_("Description"), null=True, blank=True)
    price       = MoneyField(max_digits=14,
                        decimal_places=2,
                        default_currency='USD',
                        validators=[
                            MinMoneyValidator(0),
                        ])
    price_in_points= models.IntegerField(validators=[MinValueValidator(int('0'))])
    points_rate    = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('100.0'))
        ]
    )
    valid_until = models.DateField(validators=[DateLessThanToday(now())])
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

class ActivityTag(models.Model):
    activity= models.ForeignKey(Activity, verbose_name=_("Activity"), on_delete=models.CASCADE)
    tag     = models.ForeignKey(Tag, verbose_name=_("Tag"), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
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
    
class Site(models.Model):
    photo   = AvatarField(_("Photo"), max_size=(1024, 1024),upload_to="uploads/attractions")
    address = AddressField(null=True)
    name    = models.CharField(_("Name"), max_length=50)
    description= models.TextField(_("Description"), null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    class Meta:
        ordering = ['name']
        