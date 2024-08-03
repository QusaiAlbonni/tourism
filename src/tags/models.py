from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint

class TagsCategory(models.Model):
    CATEGORY_CHOICES = [
        ('Car', 'Car'),
        ('Property', 'Property'),
        ('SupProperty', 'SupProperty'),
        ('Activity', 'Activity'),
    ]
    name = models.CharField(max_length=50 )
    type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'type'], name='unique_name_type')
        ]
    
class Tag(models.Model):
    name = models.CharField(max_length=50)
    contenttype = models.CharField(max_length=50)
    category = models.ForeignKey("TagsCategory", on_delete=models.CASCADE, related_name='tags')
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'category'], name='unique_name_category')
        ]
class SupTag(models.Model):
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)


    def save(self, *args, **kwargs):
        if hasattr(self.__class__, 'allowed_category_type') and self.tag.category.type == self.__class__.allowed_category_type:
            super().save(*args, **kwargs)
        else:
            raise ValueError(f"Category type must be '{self.__class__.allowed_category_type}' for {self.__class__.__name__}, but got '{self.tag.category.type}'.")

    class Meta:
        abstract = True

