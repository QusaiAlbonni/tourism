from celery import shared_task
from tourism.celery import app
from .models import Tour
from django.utils import timesince
from django.utils import timezone
from . import notifications as notifs
from .models import Activity
from .models import Tour, Activity, Ticket
from reservations.models import TicketPurchase
from django.db.models import Subquery

@shared_task
def send_tour_notifications_task(tour_id: int):
    tour = Tour.objects.get(pk= tour_id)
    humanized_date = timesince.timeuntil(tour.takeoff_date, timezone.now())
    notifs.send_notifications_tour_takeoff(tour, humanized_date)
    
@app.task()
def notify_users_on_crucial_update(activity_id: int):
    activity = Activity.objects.get(pk= activity_id)
    notifs.send_notifications_on_crucial_update(activity)
    
@app.task()
def notify_users_of_cancellation(activity_id: int):
    user_ids = TicketPurchase.objects.filter(owner__in=Subquery(TicketPurchase.objects.filter(ticket__activity__pk= activity_id).values('owner').distinct())).values_list('owner', flat=True).distinct()
    users = list(set(user_ids))
    
    try:
        activity = Activity.objects.get(pk = activity_id)
    except Activity.DoesNotExist:
        return "ACTIVITY DOES NOT EXIST"
    notifs.send_notification_on_cancellation(users, activity)

@app.task()
def notify_users_of_cancellation_ticket(ticket_id: int):
    user_ids = TicketPurchase.objects.filter(owner__in=Subquery(TicketPurchase.objects.filter(ticket__pk= ticket_id).values('owner').distinct())).values_list('owner', flat=True).distinct()
    users = list(set(user_ids))
    try:
        ticket = Ticket.objects.get(pk =ticket_id)
    except Ticket.DoesNotExist:
        return "TICKET DOES NOT EXIST"
    notifs.send_notification_on_cancellation(users, ticket)