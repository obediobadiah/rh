# Generated by Django 5.0.7 on 2024-09-12 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0017_remove_activityplanreport_modality_retargeting'),
        ('rh', '0031_alter_targetlocation_facility_monitoring'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityplanreport',
            name='implementing_partners',
        ),
        migrations.AddField(
            model_name='responsetype',
            name='clusters',
            field=models.ManyToManyField(to='rh.cluster'),
        ),
        migrations.AddField(
            model_name='responsetype',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='activityplanreport',
            name='response_types',
            field=models.ManyToManyField(blank=True, limit_choices_to={'is_active': True}, to='project_reports.responsetype'),
        ),
    ]
