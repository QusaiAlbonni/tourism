from django.db import models
from django.utils.translation import gettext_lazy as _

class Event(models.Model):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    description = models.TextField(blank=True, verbose_name=_("Description"), max_length=2048)
    on = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    