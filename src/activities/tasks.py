from celery import shared_task
from tourism.celery import app
from .models import Tour
from django.utils import timesince
from django.utils import timezone
from . import notifications as notifs
from .models import Activity
@shared_task
def send_tour_notifications_task(tour_id: int):
    tour = Tour.objects.get(pk= tour_id)
    humanized_date = timesince.timeuntil(tour.takeoff_date, timezone.now())
    notifs.send_notifications_tour_takeoff(tour, humanized_date)
    
@app.task()
def notify_users_on_crucial_update(activity_id: int):
    activity = Activity.objects.get(pk= activity_id)
    notifs.send_notifications_on_crucial_update(activity)