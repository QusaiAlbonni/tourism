# Generated by Django 5.0.3 on 2024-06-07 08:48

import activities.validators
import app_media.models
import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0006_tour_duration_tour_guide_tour_takeoff_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attraction',
            name='photo',
            field=app_media.models.AvatarField(default='http://localhost:8000/media/uploads/service_photos/logo_HLMuf6x.png', max_size=(1024, 1024), upload_to='', verbose_name='Photo'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attraction',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='attraction',
            name='tour',
            field=models.ForeignKey(max_length=2, on_delete=django.db.models.deletion.CASCADE, related_name='attractions', to='activities.tour', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='valid_until',
            field=models.DateField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 7, 8, 47, 42, 774553, tzinfo=datetime.timezone.utc))]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='takeoff_date',
            field=models.DateTimeField(validators=[activities.validators.DateLessThanToday(datetime.datetime(2024, 6, 7, 8, 47, 42, 772551, tzinfo=datetime.timezone.utc))], verbose_name=''),
        ),
    ]
