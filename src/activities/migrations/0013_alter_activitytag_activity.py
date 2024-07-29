# Generated by Django 5.0.3 on 2024-07-29 13:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0012_alter_activitytag_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitytag',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_tags', to='activities.activity', verbose_name='Activity'),
        ),
    ]
