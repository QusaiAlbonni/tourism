from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Service(models.Model):
    favorited_by = models.ManyToManyField(
        User,
        verbose_name= "Favorited by Users",
        through="ServiceFavorite",
        through_fields=("service", "user")
        )
    
class ServiceFavorite(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)