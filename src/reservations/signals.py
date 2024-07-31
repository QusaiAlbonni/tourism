from django.db.models.signals import post_save
from notifications.signals import notify
from django.dispatch import receiver
from .models import Refund
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .notifications import send_refund_notification as srf

@receiver(post_save, sender= Refund)
def send_refund_notification(sender, instance, created, **kwargs):
    srf(sender, instance)
    