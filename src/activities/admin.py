from django.contrib import admin
from .models import Guide
# Register your models here.

class GuideAdmin(admin.ModelAdmin):
    fields=['name', 'likes', 'bio', 'avatar']
    
admin.site.register(Guide, GuideAdmin)