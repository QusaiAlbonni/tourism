# Generated by Django 5.0.3 on 2024-06-06 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_servicereview_comment_delete_reviewcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='name',
            field=models.CharField(default='call', max_length=50, verbose_name='Name'),
            preserve_default=False,
        ),
    ]