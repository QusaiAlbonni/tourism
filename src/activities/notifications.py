from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.signals import notify
from .models import Tour, Activity
from reservations.models import TicketPurchase
from django.db.models import Subquery
from django.contrib.auth import get_user_model

User = get_user_model()

def send_notifications_tour_takeoff(tour: Tour, humanized_date: str):    
    user_ids = TicketPurchase.objects.filter(owner__in=Subquery(TicketPurchase.objects.filter(ticket__activity= tour).values('owner').distinct())).values_list('owner', flat=True).distinct()
    users = list(set(user_ids))
    
    users = User.objects.filter(pk__in= users)
    for instance in users:
        notify.send(
            instance,
            recipient=instance,
            verb=f'the tour you have purchased is starting soon',
            level= 'info',
            public=False,
            description= f"the tour you have purchased {tour.name} is starting in {humanized_date}!"
            )
    message = Message(
            notification= Notification(title= f'Your Tour is starting in {humanized_date}!', body=f"The tour you have purchased {tour.name} is starting in {humanized_date}!")
        )
    devices = FCMDevice.objects.filter(user_id__in= users)
    devices.send_message(message)
    
def send_notifications_on_crucial_update(activity):
    user_ids = TicketPurchase.objects.filter(owner__in=Subquery(TicketPurchase.objects.filter(ticket__activity= activity).values('owner').distinct())).values_list('owner', flat=True).distinct()
    users = list(set(user_ids))
    
    users = User.objects.filter(pk__in= users)
    for instance in users:
        notify.send(
            instance,
            recipient=instance,
            verb=f'the activity you are engaged with has changed',
            level= 'info',
            public=False,
            description= f"Unfortunately {activity.name} you have purchased a ticket for has had important changes to it you maybe able to fully refund your purchases"
            )
    
    message = Message(
            notification= Notification(title= f'the activity you are engaged with has changed', body=f"Unfortunately {activity.name} you have purchased a ticket for has had important changes to it you maybe able to fully refund your purchases")
        )
    devices = FCMDevice.objects.filter(user_id__in= users)
    devices.send_message(message)