# Generated by Django 5.0.3 on 2024-06-07 12:37

import activities.validators
import address.models
import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0008_alter_attraction_photo_alter_ticket_valid_until_and_more'),
        ('address', '0003_auto_20200830_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attraction',
            name='address',
            field=address.models.AddressField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='address.address'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='valid_until',
            field=models.DateField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 7, 12, 37, 20, 565429, tzinfo=datetime.timezone.utc))]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='takeoff_date',
            field=models.DateTimeField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 7, 12, 37, 20, 563428, tzinfo=datetime.timezone.utc))], verbose_name=''),
        ),
    ]