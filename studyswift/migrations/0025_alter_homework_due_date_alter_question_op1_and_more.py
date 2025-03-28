# Generated by Django 5.0.2 on 2024-03-17 14:03

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studyswift", "0024_exam_num_questions_alter_homework_due_date"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="homework",
            name="due_date",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 3, 24, 14, 3, 43, 350278)
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="op1",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="question",
            name="op2",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="question",
            name="op3",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="question",
            name="op4",
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name="ExamSubmission",
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
                ("score", models.IntegerField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "exam",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studyswift.exam",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StudentAnswer",
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
                ("answer", models.CharField(max_length=1)),
                ("is_correct", models.BooleanField(default=False)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studyswift.question",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studyswift.examsubmission",
                    ),
                ),
            ],
        ),
    ]
