from django.db import models
from django.utils.translation import gettext_lazy as _
from app_media.models import AvatarField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from address.models import Country
from django.utils.timezone import timedelta, now
from tags.models import Tag
# Create your models here.
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
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE)
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    
class Activity(models.Model):
    service = models.OneToOneField("services.Service", verbose_name=_("Service"), on_delete=models.CASCADE)
    tags    = models.ManyToManyField(
        Tag,
        verbose_name=_("Tags"),
        through="ActivityTag",
        through_fields=("activity", "tag")
        )
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
class Tour(Activity):
    pass

class Site(Activity):
    pass

class Ticket(models.Model):
    activity= models.ForeignKey(Activity, verbose_name=_("Activity"), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

class ActivityTag(models.Model):
    activity= models.ForeignKey(Activity, verbose_name=_("Activity"), on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, verbose_name=_("Tag"), on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)