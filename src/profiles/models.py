from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE, editable= False)
    
    bio            = models.TextField(blank=True,verbose_name=_("Bio"), null=True, max_length= 2048)
    marital_status = models.BooleanField(default=False, verbose_name=_("Marital Status"))
    birth_date     = models.DateField(blank=True, null=True,auto_now=False, auto_now_add=False, verbose_name=_("Birth Date"))
    num_kids       = models.IntegerField(default= 0, verbose_name=_("Number of Children"), validators=[MaxValueValidator(30)])
    
    avatar = models.ImageField(_("Avatar"), upload_to="uploads/profiles/avatars", max_length=128)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

class CreditCard():
    pass

class PointsWallet():
    pass