from django.db import models
from django.utils.translation import gettext_lazy as _
from app_media.models import AvatarField
# Create your models here.

class Guide(models.Model):
    name  = models.CharField(_("Name"), max_length=150, unique=True)
    bio   = models.TextField(_("Guide's Bio"), max_length=2048, blank=True, null=True)
    avatar= AvatarField(_("Avatar"), upload_to="uploads/guides/avatars", null=True, max_length=1024, max_size=(128, 128))