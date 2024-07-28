from modeltranslation.translator import register, TranslationOptions, translator
from .models import Property

@register(Property)
class PropertyTranslationOptions(TranslationOptions):
    fields = ()