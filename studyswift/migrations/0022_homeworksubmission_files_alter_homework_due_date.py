# Generated by Django 5.0.2 on 2024-03-16 20:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studyswift", "0021_alter_homework_due_date_rewardpurchase"),
    ]

    operations = [
        migrations.AddField(
            model_name="homeworksubmission",
            name="files",
            field=models.ManyToManyField(
                blank=True,
                related_name="submission_files",
                to="studyswift.homeworkfile",
            ),
        ),
        migrations.AlterField(
            model_name="homework",
            name="due_date",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 3, 23, 20, 25, 8, 415307)
            ),
        ),
    ]
