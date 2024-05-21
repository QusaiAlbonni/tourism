from django.db import models
from django.core.exceptions import ValidationError

class TagsCategoryPermission(models.Model):
    name = models.CharField(max_length=50 , unique=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)

class TagsCategory(models.Model):
    name = models.CharField(max_length=50 , unique=True)
    role = models.ForeignKey("TagsCategoryPermission",on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)
    
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    contenttype = models.CharField(max_length=50)
    category = models.ForeignKey("TagsCategory", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable= False)
    modified= models.DateTimeField(auto_now=True, auto_now_add=False, editable= False)


class SupTag(models.Model):
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE)
    class Meta:
        abstract = True
    
    def save(self,*args,**kwargs):
        role_names = self.tag.category.role.name
        if self.__class__.__name__  != role_names and role_names!='all_permission':
            raise ValidationError(f"The name of the current model ({self.__class__.__name__}) does not match any of the associated TagsCategoryPermission names ({role_names}).")
        
        super().save(*args, **kwargs)
