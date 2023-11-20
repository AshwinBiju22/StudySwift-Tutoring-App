# Generated by Django 3.2.22 on 2023-11-20 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('studyswift', '0002_delete_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoomMeeting',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('topic', models.CharField(max_length=255)),
                ('join_url', models.URLField()),
                ('password', models.CharField(max_length=50)),
            ],
        ),
    ]
