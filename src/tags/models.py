from django.db import models
from django.core.exceptions import ValidationError

class TagsCategory(models.Model):
    name = models.CharField(max_length=50 , unique=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    contenttype = models.CharField(max_length=50)
    category = models.ForeignKey("TagsCategory", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)


class SupTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    class Meta:
        abstract = True
