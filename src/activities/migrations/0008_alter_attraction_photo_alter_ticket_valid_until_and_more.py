# Generated by Django 5.0.3 on 2024-06-07 11:53

import activities.validators
import app_media.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0007_attraction_photo_alter_attraction_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attraction',
            name='photo',
            field=app_media.models.AvatarField(max_size=(1024, 1024), upload_to='uploads/attractions', verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='valid_until',
            field=models.DateField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 7, 11, 53, 44, 349062, tzinfo=datetime.timezone.utc))]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='takeoff_date',
            field=models.DateTimeField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 7, 11, 53, 44, 347062, tzinfo=datetime.timezone.utc))], verbose_name=''),
        ),
    ]