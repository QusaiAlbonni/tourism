# Generated by Django 5.0.3 on 2024-06-28 10:56

import activities.validators
import datetime
import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0005_ticket_stock_alter_listing_work_hours_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': 'Activity', 'verbose_name_plural': 'Activities'},
        ),
        migrations.AlterField(
            model_name='ticket',
            name='points_rate',
            field=models.DecimalField(decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('1.0')), django.core.validators.MaxValueValidator(Decimal('100.0'))]),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='price_in_points',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='valid_until',
            field=models.DateField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 28, 10, 56, 33, 653981, tzinfo=datetime.timezone.utc))]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='takeoff_date',
            field=models.DateTimeField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 28, 10, 56, 33, 651981, tzinfo=datetime.timezone.utc))], verbose_name=''),
        ),
    ]