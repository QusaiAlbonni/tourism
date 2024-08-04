from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from modeltranslation.translator import translator as model_translator
from .utils import translate_fields
from activities.models import Tour, Listing, Ticket
from properties.models import Property

@receiver(pre_save, sender= Tour)
@receiver(pre_save, sender=Listing)
@receiver(pre_save, sender=Property)
@receiver(pre_save, sender=Ticket)
def auto_translate_fields(sender, instance, **kwargs):
    if instance.pk:
        return
    fields = model_translator.get_options_for_model(sender).get_field_names()
    translate_fields(instance, fields)
    
    
    