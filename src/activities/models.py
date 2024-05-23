from django.db import models
from django.utils.translation import gettext_lazy as _
from app_media.models import AvatarField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from address.models import Country
# Create your models here.
User = get_user_model()

class Guide(models.Model):
    name  = models.CharField(_("Name"), max_length=150, unique=True)
    bio   = models.TextField(_("Guide's Bio"), max_length=2048, blank=True, null=True)
    avatar= AvatarField(_("Avatar"), upload_to="uploads/guides/avatars" , null=True, max_length=1024, max_size=(128, 128))
    email = models.EmailField(_("Email"), blank=True, null=True)
    
    #country = models.ForeignKey(Country, verbose_name=_("Country Of origins"), on_delete=models.SET_NULL, blank=True, null=True)
    
    #available = models.BooleanField(_("Availability"), default=True)
    
    likers = models.ManyToManyField(User, verbose_name=_(""))
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    class Meta:
        ordering = ["-created"]
    
    @property
    def likes(self):
        return self.likers.count()
    
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

from tags.models import SupTag

class ActivityTag(SupTag):
    # activites_id
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)