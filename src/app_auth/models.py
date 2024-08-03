from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
# from profiles.models import PointsWallet

# Create your models here.

# pw for pingoway
class pwUserManager(UserManager):
    def get_by_natural_key(self, username):
        user = self.get(
            Q(**{self.model.USERNAME_FIELD: username}) |
            Q(**{self.model.EMAIL_FIELD: username})
        )
        return user

    
class User(AbstractUser):
    is_admin = models.BooleanField(default=False, verbose_name='admin status', help_text='checks if the user is an admin of the establishment site')
    email = models.EmailField( unique=True,verbose_name='email address', max_length=254)
    objects = pwUserManager()
    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS=['username']

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = (
            ('manage_activities', 'Can manage Activities'),
            ('manage_properties', 'Can manage properties'),
            ('manage_car_rental', 'Can manage Car Rental')
        )
        
    def get_avatar(user):
        try:
            return user.profile.avatar.url
        except ValueError as e:
            return ""