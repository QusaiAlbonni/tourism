# Generated by Django 5.0.3 on 2024-07-14 15:31

import activities.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_alter_ticket_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='opens_at',
            field=models.TimeField(verbose_name='Opens At Time'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='activities.site', verbose_name='Site'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='takeoff_date',
            field=models.DateTimeField(validators=[activities.validators.DateLessThanToday(1)], verbose_name='Takeoff date'),
        ),
    ]
