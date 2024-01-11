# Generated by Django 4.0.6 on 2024-01-09 07:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0015_remove_targetlocation_title_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="indicator",
            name="code",
        ),
        migrations.AlterField(
            model_name="activitydetail",
            name="code",
            field=models.CharField(max_length=600),
        ),
        migrations.AlterField(
            model_name="activitydetail",
            name="name",
            field=models.CharField(max_length=600),
        ),
        migrations.AlterField(
            model_name="activitytype",
            name="name",
            field=models.CharField(max_length=600),
        ),
        migrations.AlterField(
            model_name="indicator",
            name="name",
            field=models.CharField(max_length=600),
        ),
        migrations.AddConstraint(
            model_name="activitydetail",
            constraint=models.UniqueConstraint(
                fields=("code", "activity_type"), name="unique_ActivityDetail_for_activity_type"
            ),
        ),
        migrations.AddConstraint(
            model_name="activitytype",
            constraint=models.UniqueConstraint(
                fields=("code", "activity_domain"), name="unique_activitytype_for_activity_domain"
            ),
        ),
    ]
