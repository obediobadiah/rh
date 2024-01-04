# Generated by Django 4.0.6 on 2024-01-04 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0013_targetlocation_facility_site_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityplan',
            name='title',
        ),
        migrations.AlterField(
            model_name='organization',
            name='code',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='code',
            field=models.CharField(max_length=200),
        ),
    ]
