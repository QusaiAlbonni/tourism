from django.contrib import admin
from .models import Guide, GuideLiker, Activity
from django.db.models import ManyToManyField, DateField
# Register your models here.

class GuideAdmin(admin.ModelAdmin):
    fields=['name', 'bio', 'avatar']
    list_display= ('name', 'bio', 'likes')
    
admin.site.register(Guide, GuideAdmin)

class GuideLikerAdmin(admin.ModelAdmin):
    fields=['guide', 'user']
    list_display= ('guide', 'user')
    
admin.site.register(GuideLiker, GuideLikerAdmin)


class ActivityAdmin(admin.ModelAdmin):
    fields= [field.name for field in Activity._meta.get_fields() if not isinstance(field, ManyToManyField) and not isinstance(field, DateField)]
    
admin.site.register(Activity, ActivityAdmin)