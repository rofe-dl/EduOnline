from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Subject(models.Model):
    subject_name = models.CharField(max_length=255, primary_key=True)
    avg_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject_name