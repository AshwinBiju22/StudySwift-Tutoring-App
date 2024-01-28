import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import random, string
from datetime import datetime, timedelta
from django.utils import timezone

class Reward(models.Model):
    name = models.CharField(max_length=100)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    good_points = models.IntegerField(default=0)
    bad_points = models.IntegerField(default=0)
    rewards = models.ManyToManyField(Reward, related_name='reward_locker', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username.capitalize()

class Flashcard(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    subject = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class SchoolClass(models.Model):
    code = models.CharField(max_length=4, unique=True, blank=True)
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes_taught', null=True, blank=True)
    students = models.ManyToManyField(User, related_name='classes_enrolled', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a random 4-character code
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        super().save(*args, **kwargs)

    def add_student(self, student):
        self.students.add(student)

    def add_teacher(self, teacher):
        self.teacher = teacher

    def remove_student(self, student):
        self.students.remove(student)

    def remove_teacher(self):
        self.teacher = None

class HomeworkFile(models.Model):
    file = models.FileField(upload_to='teacher_uploads/', null=True, blank=True)

    def delete(self, *args, **kwargs):
        # Delete the file from the storage when the HomeworkFile is deleted
        if self.file:
            file_path = os.path.join(settings.MEDIA_ROOT, str(self.file))
            if os.path.exists(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return str(self.file)

class HomeworkSubmission(models.Model):
    file = models.FileField(upload_to='student_uploads/', null=True, blank=True)
    completed = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_submissions')
    homework = models.ForeignKey('Homework', on_delete=models.CASCADE, related_name='homework_submissions')

    def delete(self, *args, **kwargs):
        # Delete the file from the storage when the HomeworkFile is deleted
        if self.file:
            file_path = os.path.join(settings.MEDIA_ROOT, str(self.file))
            if os.path.exists(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return str(self.file)

class Homework(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='homework')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateTimeField(default=datetime.now() + timedelta(days=7))
    files = models.ManyToManyField(HomeworkFile, related_name='homework_files', blank=True)
    submissions = models.ManyToManyField(HomeworkSubmission, related_name='homework_submissions', blank=True)


    
    