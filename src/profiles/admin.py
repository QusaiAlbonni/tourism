from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Profile, CreditCard

class ProfileAdmin(admin.ModelAdmin):
    fields = ['bio', 'marital_status', 'birth_date', 'num_kids', 'avatar', 'address']

class CardAdmin(admin.ModelAdmin):
    fields = ['balance', 'user']

admin.site.register(Profile, ProfileAdmin)

admin.site.register(CreditCard, CardAdmin)