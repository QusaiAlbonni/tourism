from celery import shared_task
from .models import Tour
from django.utils import timesince
from django.utils import timezone
from . import notifications as notifs

@shared_task
def send_tour_notifications_task(tour_id: int):
    tour = Tour.objects.get(pk= tour_id)
    humanized_date = timesince.timeuntil(tour.takeoff_date, timezone.now())
    notifs.send_notifications_tour_takeoff(tour, humanized_date)