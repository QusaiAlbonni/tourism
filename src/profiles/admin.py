from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    fields = ['bio', 'marital_status', 'birth_date', 'num_kids', 'avatar', 'address']


admin.site.register(Profile, ProfileAdmin)
