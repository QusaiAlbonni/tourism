# Generated by Django 5.0.3 on 2024-05-02 16:21

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=2048, null=True, verbose_name='Bio')),
                ('marital_status', models.BooleanField(default=False, verbose_name='Marital Status')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Birth Date')),
                ('num_kids', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(30)], verbose_name='Number of Children')),
                ('avatar', models.ImageField(max_length=128, upload_to='uploads/profiles/avatars', verbose_name='Avatar')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
