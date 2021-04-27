from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Subject(models.Model):
    subject_name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.subject_name

class Exam(models.Model):
    exam_id = models.CharField(max_length=255, primary_key=True)
    exam_name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField(default=0)
    standard = models.PositiveSmallIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.exam_name

class Question(models.Model):
    question_id = models.CharField(max_length=255, primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    statement = models.CharField(max_length=1024)
    solution_id = models.CharField(max_length=255) #storing solution_id and not solution because solution not defined yet
    mark = models.PositiveIntegerField()

    def __str__(self):
        return self.statement

class Choice(models.Model):
    choice_id = models.CharField(max_length=255, primary_key=True)
    answer = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.answer

