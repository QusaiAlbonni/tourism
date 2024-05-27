from django.contrib import admin
from .models import Guide, GuideLiker
# Register your models here.

class GuideAdmin(admin.ModelAdmin):
    fields=['name', 'bio', 'avatar']
    list_display= ('name', 'bio', 'likes')
    
admin.site.register(Guide, GuideAdmin)

class GuideLikerAdmin(admin.ModelAdmin):
    fields=['guide', 'user']
    list_display= ('guide', 'user')
    
admin.site.register(GuideLiker, GuideLikerAdmin)