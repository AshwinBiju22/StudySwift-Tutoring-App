from django.db import models
from django.contrib.auth.models import User
import random, string
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

class File(models.Model):
    file = models.FileField(upload_to='homework_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Homework(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    files = models.ManyToManyField(File, blank=True)

class HomeworkSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    files = models.ManyToManyField(File, related_name='submission_files', blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)