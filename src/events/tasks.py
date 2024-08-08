from celery import shared_task
from .models import Event
from . import notifications as notifs

@shared_task
def event_activate(event_id):
    event = Event.objects.get(id=event_id)
    event.activate = True
    event.save()
    
    notifs.notify_users_of_event(event)
    return f"Event {event.id} activated"

@shared_task
def event_deactivate(event_id):
    event = Event.objects.get(id=event_id)
    event.activate = False
    event.save()
    
    notifs.notify_users_of_event_end(event)
    return f"Event {event.id} activated"

    