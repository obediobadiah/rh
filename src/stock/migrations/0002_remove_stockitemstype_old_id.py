# Generated by Django 4.0.6 on 2024-03-20 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockitemstype',
            name='old_id',
        ),
    ]
