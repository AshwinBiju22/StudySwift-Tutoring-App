# Generated by Django 3.2.22 on 2024-01-27 22:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studyswift', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='homework',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 3, 22, 2, 58, 145935)),
        ),
    ]
