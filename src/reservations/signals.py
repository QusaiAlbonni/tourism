from django.db.models.signals import post_save
from notifications.signals import notify
from django.dispatch import receiver
from .models import Refund, TicketPurchase
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .notifications import send_refund_notification as srf, send_purchase_success_notification

@receiver(post_save, sender= Refund)
def send_refund_notification(sender, instance, created, **kwargs):
    srf(sender, instance)
    
@receiver(post_save, sender= TicketPurchase)
def notify_user_of_his_purchase(sender, instance, created, **kwargs):
    if instance.pk:
        return
    send_purchase_success_notification(instance)
    
    