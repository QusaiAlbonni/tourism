from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db.models import Q
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