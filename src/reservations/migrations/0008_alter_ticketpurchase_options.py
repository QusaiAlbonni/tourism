# Generated by Django 5.0.3 on 2024-07-14 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0007_ticketpurchase_qr_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticketpurchase',
            options={'ordering': ['-created'], 'permissions': (('scan_reservations', 'Can scan resrvations'),)},
        ),
    ]
