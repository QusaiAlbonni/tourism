from .models import Refund
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.signals import notify

def send_refund_notification_bulk(refunds):
    users = []
    refunds = Refund.objects.filter(id__in= refunds)
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
    
def send_gifted_points_notification(user, amount_gifted):
    notify.send(
        sender= user,
        recipient= user,
        verb=f'you have been gifted {amount_gifted} points!',
        level= 'success',
        public=False,
        description= f"your you have been gifted the amount {amount_gifted} points! spend it wisely"
        )
    message = Message(
        notification= Notification(title= f'you have been gifted {amount_gifted} points!', body=f"your you have been gifted the amount {amount_gifted} points! spend it wisely")
    )
    devices = FCMDevice.objects.filter(user = user)
    devices.send_message(message)
    
def send_successful_scanning_notification(instance):
    notify.send(
        sender= instance.owner,
        recipient=instance.owner,
        verb='your ticket has been scanned!',
        level= 'success',
        public=False,
        description= f"your purchase for {instance.ticket} for {instance.ticket.activity.name} has been scanned!"
        )
    message = Message(
        notification= Notification(title= 'your ticket has been scanned!', body=f"your purchase for {instance.ticket} for {instance.ticket.activity.name} has been scanned!")
    )
    devices = FCMDevice.objects.filter(user = instance.owner)
    devices.send_message(message)
