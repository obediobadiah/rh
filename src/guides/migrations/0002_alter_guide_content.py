# Generated by Django 5.0.6 on 2024-07-18 05:21

import mdeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guide',
            name='content',
            field=mdeditor.fields.MDTextField(),
        ),
    ]
