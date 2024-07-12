# myapp/management/commands/add_periodic_task.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Add a periodic task to Celery Beat'

    def handle(self, *args, **kwargs):
        # Create the interval schedule
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS,
        )

        # Create the periodic task
        PeriodicTask.objects.create(
            interval=schedule,
            name='Sample Task Every 10 Seconds',
            task='app_auth.tasks.sample_task',
        )

        self.stdout.write(self.style.SUCCESS('Successfully added periodic task'))
