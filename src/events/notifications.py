from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.signals import notify
from django.contrib.auth import get_user_model
from .models import Event
User = get_user_model()

def notify_users_of_event(event: Event):
    notify.send(
        event,
        recipient=User.objects.all(),
        verb=f'the event {event.name} has started',
        level= 'info',
        public=False,
        description= f"{event.description}!"
    )
        
    message = Message(
            notification= Notification(title= f'the event {event.name} has started!', body=f"{event.description}!")
        )
    devices = FCMDevice.objects.filter(user_id__in= list(User.objects.all()))
    devices.send_message(message)
    
def notify_users_of_event_end(event: Event):
    notify.send(
        event,
        recipient=User.objects.all(),
        verb=f'the event {event.name} has ended',
        level= 'info',
        public=False,
        description= f"{event.description}!"
    )
        
    message = Message(
            notification= Notification(title= f'the event {event.name} has ended!, hope you enjoyed it!', body=f"{event.description}!")
        )
    devices = FCMDevice.objects.filter(user_id__in= list(User.objects.all()))
    devices.send_message(message)