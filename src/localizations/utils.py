from django.conf import settings
from django.db.models import Model
from modeltranslation.utils import build_localized_fieldname
from tourism.utils import rgetattr, rsetattr
from deep_translator import GoogleTranslator


google_translator = settings.GOOGLE_TRANSLATE

langs = settings.MODELTRANSLATION_LANGUAGES

default_lang = settings.MODELTRANSLATION_DEFAULT_LANGUAGE


def translate_fields(instance: Model, fields: list):
    for field in fields:
        default_value = rgetattr(instance, field)
        for lang in langs:
            if lang is default_lang:
                continue
            field_name = build_localized_fieldname(field, lang)
            translated_value = google_translator(source='auto', target=lang).translate(default_value)
            rsetattr(instance, field_name, translated_value)
            
            
        