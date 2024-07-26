from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import Ticket, Activity, Tour, Listing, TourSite
from django.utils import timezone
from tourism.utils import rgetattr, rsetattr

@receiver(pre_save, sender=Ticket)    
@receiver(pre_save, sender=Tour)
@receiver(pre_save, sender=Listing)
@receiver(pre_save, sender=TourSite)
def trigger_on_update(sender, instance, **kwargs):
    return on_crucial_field_update(sender, instance, **kwargs)


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
        
    return
    
    
def changed_crucial_fields(instance, old_instance, fields):
    updated_fields = {}
    
    for field in fields:
        old_value = rgetattr(old_instance, field)
        new_value = rgetattr(instance, field)
        
        if old_value != new_value:
            updated_fields[field] = {'old_value': old_value, 'new_value': new_value}
            
    return updated_fields
    