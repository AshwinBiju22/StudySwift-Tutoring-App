# Generated by Django 5.0.2 on 2024-03-17 11:09

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studyswift", "0022_homeworksubmission_files_alter_homework_due_date"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="homework",
            name="due_date",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 3, 24, 11, 9, 48, 944115)
            ),
        ),
        migrations.CreateModel(
            name="Exam",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "assigned_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studyswift.schoolclass",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question", models.TextField()),
                ("op1", models.TextField()),
                ("op2", models.TextField()),
                ("op3", models.TextField()),
                ("op4", models.TextField()),
                ("answer", models.CharField(max_length=1)),
                ("marks", models.IntegerField(default=1)),
                (
                    "exam",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studyswift.exam",
                    ),
                ),
            ],
        ),
    ]
