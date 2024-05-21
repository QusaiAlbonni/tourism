from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import TagsCategoryPermission

@receiver(post_migrate)
def create_default_permission(sender, **kwargs):
    if not TagsCategoryPermission.objects.filter(name="all_permission").exists():
        TagsCategoryPermission.objects.create(name="all_permission")

