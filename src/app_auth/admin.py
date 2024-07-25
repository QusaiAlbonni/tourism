from django.utils.crypto import get_random_string
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password

class pwUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    
    fieldsets = (
        (None, {"fields": ("email",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "username")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_admin",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "is_admin"),
            },
        ),
    )
    
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_admin")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "is_admin")

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            # read doc for this function and if ther is another one god more than this put it
            # random_password = make_password(None)
            random_password = '1234wasdf!@#$'
            obj.set_password(random_password)
            
            
            super().save_model(request, obj, form, change)
            
            obj.email_user('Your new account password', f'Your new account password is: {random_password}')
        else:
            super().save_model(request, obj, form, change)

admin.site.register(User, pwUserAdmin)