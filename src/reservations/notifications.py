from .models import Refund
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.signals import notify

def send_refund_notification_bulk(refunds):
    users = []
    refunds = Refund.objects.filter(id__in= refunds)
    print(refunds)
    for instance in refunds:
        notify.send(
            instance.reservation.first().owner,
            recipient=instance.reservation.first().owner,
            verb='you have been refunded',
            level= 'success',
            public=False,
            description= f"you have been refunded the amount {instance.amount.amount} {instance.amount.currency}"
            )
        message = Message(
            notification= Notification(title= 'You have been refunded!', body=f"you have been refunded the amount {instance.amount.amount} {instance.amount.currency}")
        )
        user = instance.reservation.first().owner.id
    
        devices = FCMDevice.objects.filter(user_id= user)
        devices.send_message(message)
    
def send_refund_notification(sender, instance):
    notify.send(
        sender= instance.reservation.first().owner,
        recipient=instance.reservation.first().owner,
        verb='you have been refunded',
        level= 'success',
        public=False,
        description= f"you have been refunded the amount {instance.amount.amount} {instance.amount.currency}"
        )
    message = Message(
        notification= Notification(title= 'You have been refunded!', body=f"you have been refunded the amount {instance.amount.amount} {instance.amount.currency}")
    )
    devices = FCMDevice.objects.filter(user = instance.reservation.first().owner)
    devices.send_message(message)

def send_purchase_success_notification(instance):
    notify.send(
        sender= instance.owner,
        recipient=instance.owner,
        verb='your purchase have went through',
        level= 'success',
        public=False,
        description= f"your purchase for {instance.ticket} for {instance.ticket.activity.name} have went through"
        )
    message = Message(
        notification= Notification(title= 'your purchase have went through', body=f"your purchase for {instance.ticket} for {instance.ticket.activity.name} have went through")
    )
    devices = FCMDevice.objects.filter(user = instance.owner)
    devices.send_message(message)
