from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask

class Event(models.Model):
    TYPE=[
       ('Daily','Daily'),
       ('Weekly','Weekly'),
       ('Monthly','Monthly'),
       ('Yearly','Yearly'),
    ]
    name = models.CharField(_("Name"), max_length=50, unique=True)
    description = models.TextField(blank=True, verbose_name=_("Description"), max_length=2048)
    activate = models.BooleanField(default=False)
    type = models.CharField(max_length=30,choices=TYPE)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        permissions = [
            ("manage_event", "Can manage event"),
        ]
        
    def __str__(self):
        return self.name
    
    
class EventPeriodicTask(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='periodic_tasks')
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)