from celery import shared_task
from .models import Event

@shared_task
def event_activate(event_id):
    event = Event.objects.get(id=event_id)
    event.activate = True
    event.save()
    return f"Event {event.id} activated"

@shared_task
def event_deactivate(event_id):
    event = Event.objects.get(id=event_id)
    event.activate = False
    event.save()
    return f"Event {event.id} activated"

    