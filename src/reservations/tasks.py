from celery import shared_task
from tourism.celery import app
from .notifications import send_refund_notification_bulk

@app.task()
def send_refund_notifications_task(refunds):
    send_refund_notification_bulk(refunds)