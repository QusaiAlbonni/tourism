# Generated by Django 5.0.3 on 2024-07-03 19:36

import activities.validators
import datetime
import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0007_rename_price_in_points_ticket_points_discount_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='points_discount',
            field=models.DecimalField(decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.0')), django.core.validators.MaxValueValidator(Decimal('100.0'))]),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='valid_until',
            field=models.DateField(validators=[activities.validators.DateLessThanToday(1)]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='takeoff_date',
            field=models.DateTimeField(validators=[activities.validators.DateLessThanToday(1)], verbose_name=''),
        ),
    ]