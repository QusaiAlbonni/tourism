from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'is_admin')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(None)  
        if commit:
            user.save()
        return user