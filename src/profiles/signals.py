from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PointsWallet, Profile
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        PointsWallet.objects.create(user=instance, num_points=10)
        
@receiver(post_save, sender=User)
def my_handler(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user= instance)