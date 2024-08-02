from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.signals import notify
from .models import Tour


def send_notifications_tour_takeoff(tour: Tour, humanized_date: str):
    purchases = tour.tickets.purchases.all()
    
    users = []
    for instance in purchases:
        notify.send(
            instance.owner,
            recipient=instance.owner,
            verb=f'the tour you have purchased is starting soon',
            level= 'info',
            public=False,
            description= f"the tour you have purchased {tour.name} is starting in {humanized_date}!"
            )
        
        users.append(instance.owner.id)
    message = Message(
            notification= Notification(title= f'Your Tour is starting in {humanized_date}!', body=f"The tour you have purchased {tour.name} is starting in {humanized_date}!")
        )
    devices = FCMDevice.objects.filter(user_id__in= users)
    devices.send_message(message)