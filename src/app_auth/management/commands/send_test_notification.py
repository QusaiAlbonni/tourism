
from django.core.management.base import BaseCommand
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from notifications.signals import notify
from django.contrib.auth import get_user_model
User = get_user_model()

class Command(BaseCommand):
    help = "send a test notification"
    
    def handle(self, *args, **kwargs):
        message = Message(
                notification= Notification(title= f'Test notification')
            )
        devices = FCMDevice.objects.all()
        devices.send_message(message)
        self.stdout.write(self.style.SUCCESS('Successfully sent a notification'))