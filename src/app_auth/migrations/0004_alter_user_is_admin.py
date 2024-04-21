# Generated by Django 5.0.3 on 2024-04-21 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0003_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, editable=False, help_text='checks if the user is an admin of the establishment site', verbose_name='admin status'),
        ),
    ]
