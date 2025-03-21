# Generated by Django 5.0.2 on 2024-03-14 18:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "studyswift",
            "0019_homeworkfile_studentfile_alter_homework_due_date_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="homework",
            name="due_date",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 3, 21, 18, 25, 20, 648689)
            ),
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="rewards",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="rewards",
            field=models.ManyToManyField(
                blank=True, related_name="reward_locker", to="studyswift.reward"
            ),
        ),
    ]
