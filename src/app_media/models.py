from django.core.files.base import File
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image
from io import BytesIO

# Create your models here.
class AvatarFieldFile(ImageFieldFile):
    max_size = (256, 256)
    def save(self, name: str, content: File, save: bool) -> None:
        img = Image.open(self)
        img.thumbnail(self.max_size)
        
        thumb_io = BytesIO()
        
        img.save(thumb_io, img.format, quality=100)
        
        content.file = thumb_io
        return super().save(name, content, save)
class AvatarField(models.ImageField):
    attr_class = AvatarFieldFile