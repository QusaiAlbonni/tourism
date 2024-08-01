from notifications.models import Notification
from rest_framework import serializers
from django.utils import timesince
from django.utils.timezone import now

class NotificationSerializer(serializers.ModelSerializer):
    humanized_timestamp = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ('id', 'level', 'verb', 'description', 'timestamp','humanized_timestamp', 'data', 'unread')
        
    def get_humanized_timestamp(self, obj):
        return timesince.timesince(obj.timestamp, now=now())