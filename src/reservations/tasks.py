from celery import shared_task
from tourism.celery import app
from .models import TicketPurchase
from .notifications import send_refund_notification_bulk, send_gifted_points_notification, send_purchase_success_notification, send_successful_scanning_notification
from .models import get_user_model

@app.task()
def send_refund_notifications_task(refunds):
    send_refund_notification_bulk(refunds)
    
    
@app.task()
def send_gifted_points_notification_task(user_id, amount_gifted):
    user = get_user_model().objects.get(pk= user_id)
    send_gifted_points_notification(user, amount_gifted)
    

@app.task()
def send_successful_scanning_notification_task(purchase_id):
    purchase = TicketPurchase.objects.get(pk= purchase_id)
    send_successful_scanning_notification(purchase)    
    