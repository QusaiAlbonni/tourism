# Generated by Django 5.0.3 on 2024-06-04 18:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0004_site_opens_at_site_work_hours_ticket_points_rate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='activities.activity', verbose_name='Activity'),
        ),
    ]