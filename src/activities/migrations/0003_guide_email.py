# Generated by Django 5.0.3 on 2024-05-17 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_rename_likes_guide_likers'),
    ]

    operations = [
        migrations.AddField(
            model_name='guide',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
    ]
