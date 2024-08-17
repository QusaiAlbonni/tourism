from django.contrib import admin
from .models import Guide, GuideLiker, Activity, Site
from django.db.models import ManyToManyField, DateField
# Register your models here.

class GuideAdmin(admin.ModelAdmin):
    fields=['name', 'bio', 'avatar', 'email']
    list_display= ('name', 'bio', 'likes')
    
admin.site.register(Guide, GuideAdmin)

class GuideLikerAdmin(admin.ModelAdmin):
    fields=['guide', 'user']
    list_display= ('guide', 'user')
    
admin.site.register(GuideLiker, GuideLikerAdmin)


class SiteAdmin(admin.ModelAdmin):
    fields= ['name', 'photo', 'description']
    
admin.site.register(Site, SiteAdmin)