from typing import Iterable, Optional
from django.db import models
from django.utils.translation import gettext_lazy as _
from .__init__ import gemini, version, genai

# Create your models here.


class GeminiResponse(models.Model):
    content = models.TextField(_('Content made by Gemini'), max_length= 4096)
    prompt  = models.TextField(_('Prompt for the AI'))
    temperature = models.FloatField(_('Sensitivity of the ai'))
    model       = models.CharField(_('The model of the AI'), max_length= 256)
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    
    
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        return super().save(force_insert, force_update, using, update_fields)