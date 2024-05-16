from django.core.files.base import File
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image
from io import BytesIO

# Create your models here.
class AvatarFieldFile(ImageFieldFile):
    def __init__(self, instance, field, name):
        self.max_size = field.max_size
        super().__init__(instance, field, name)
        
    def save(self, name: str, content: File, save: bool) -> None:
        img = Image.open(self)
        if self.max_size is not None:
            img.thumbnail(self.max_size)
        
        thumb_io = BytesIO()
        
        img.save(thumb_io, img.format, quality=100)
        
        content.file = thumb_io
        return super().save(name, content, save)
class AvatarField(models.ImageField):
    attr_class = AvatarFieldFile
    
    def __init__(self,
        verbose_name=None,
        name=None,
        width_field=None,
        height_field=None,
        **kwargs):
        self.max_size = kwargs.pop("max_size", None)
        super().__init__(verbose_name, name, width_field, height_field, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["max_size"] = self.max_size
        return name, path, args, kwargs