import json
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import Ticket, Activity, Tour, Listing, TourSite
from django.utils import timezone
from tourism.utils import rgetattr, rsetattr
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from . import tasks

@receiver(post_save, sender=Tour)
def register_notifications_for_tour_takeoff(sender, instance, **kwargs):
    if instance.pk:
        return
    date = instance.takeoff_date - timezone.timedelta(days= 1)
    now = False
    if date < timezone.now():
        now = True
        
    create_takeoff_task(instance, date, now)

def create_takeoff_task(tour: Tour, task_date: timezone.datetime, now : bool = False):
    if now:
        try:
            tasks.send_tour_notifications_task.delay(tour.pk)
        except Exception:
            return 
        return
    schedule, created = ClockedSchedule.objects.get_or_create(
        clocked_time=task_date
    )
    PeriodicTask.objects.create(
        clocked=schedule,
        name=f'sending notifs to remind users of tour take off {tour.pk}',
        task='activities.tasks.send_tour_notifications_task',
        kwargs=json.dumps({
            'tour': tour.pk,
        }),
        enabled=True,
        one_off=True,
    )
  




@receiver(pre_save, sender=Ticket)    
@receiver(pre_save, sender=Tour)
@receiver(pre_save, sender=Listing)
@receiver(pre_save, sender=TourSite)
def trigger_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    fields: dict = on_crucial_field_update(sender, instance, **kwargs)
    if len(fields):
        try:
            tasks.notify_users_on_crucial_update.delay(instance.pk)
        except Exception:
            pass
    if (sender is Tour) and ('takeoff_date' in fields):
        try:
            notif_task = PeriodicTask.objects.get(kwargs= json.dumps({
                'tour': instance.pk,
            }))
            notif_task.delete()
        except PeriodicTask.DoesNotExist as e:
            pass
        date = instance.takeoff_date - timezone.timedelta(days= 1)
        now = False
        if date < timezone.now():
            now = True
        create_takeoff_task(instance, date, now)
        

    return fields


#delete should be called in a transaction.atomic context
@receiver(pre_delete, sender= TourSite)
def trigger_on_delete(sender, instance, **kwargs):
    return on_crucial_field_delete(sender, instance, **kwargs)



    
    
    
    
    
def on_crucial_field_delete(sender, instance, **kwargs):
    if not instance.pk:
        return
    rsetattr(instance, instance.SensitiveMeta.critical_update_datefield, timezone.now())
    save_model_name = getattr(instance.SensitiveMeta, 'date_field_model', None)
    if save_model_name is not None:
        save_model = rgetattr(instance, save_model_name, None)
    else:
        save_model = instance
    save_model.save()
    
def on_crucial_field_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    updated_fields = changed_crucial_fields(instance, old_instance, sender.SensitiveMeta.critical_fields)
    
    if updated_fields:
        rsetattr(instance, instance.SensitiveMeta.critical_update_datefield, timezone.now())
        
    return updated_fields
    
    
def changed_crucial_fields(instance, old_instance, fields):
    updated_fields = {}
    
    for field in fields:
        old_value = rgetattr(old_instance, field)
        new_value = rgetattr(instance, field)
        
        if old_value != new_value:
            updated_fields[field] = {'old_value': old_value, 'new_value': new_value}
            
    return updated_fields
    