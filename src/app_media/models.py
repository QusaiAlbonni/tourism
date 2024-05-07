from django.db import models
from django.db.models.fields.files import ImageFieldFile

# Create your models here.
class AvatarFieldFile(ImageFieldFile):
   def lolo(self):
        print("this is lolo") 

class AvatarField(models.ImageField):
    attr_class = AvatarFieldFile