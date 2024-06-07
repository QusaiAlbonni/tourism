# Generated by Django 5.0.3 on 2024-06-04 11:47

import datetime
import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_activity_tour_activitytag_activity_tags_ticket_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='opens_at',
            field=models.TimeField(default=datetime.time(14, 45, 2, 491041), verbose_name=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='work_hours',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='points_rate',
            field=models.DecimalField(decimal_places=1, default=77, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.0')), django.core.validators.MaxValueValidator(Decimal('100.0'))]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='price_in_points',
            field=models.IntegerField(default=90, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='valid_until',
            field=models.DateField(default=datetime.datetime(2024, 6, 4, 19, 17, 22, 418421)),
            preserve_default=False,
        ),
    ]
