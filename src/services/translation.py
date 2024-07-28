from modeltranslation.translator import register, TranslationOptions, translator
from .models import Service


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('description', 'name')
    
    
