# Generated by Django 5.0.3 on 2024-07-11 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('contenttype', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TagsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('Car', 'Car'), ('Property', 'Property'), ('SupProperty', 'SupProperty'), ('Activity', 'Activity')], max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='tagscategory',
            constraint=models.UniqueConstraint(fields=('name', 'type'), name='unique_name_type'),
        ),
        migrations.AddField(
            model_name='tag',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tags.tagscategory'),
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('name', 'category'), name='unique_name_category'),
        ),
    ]
