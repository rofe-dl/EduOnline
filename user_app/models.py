from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from admin_app.models import *


class SubmittedAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_answer = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return self.submitted_answer.answer

class ReportCard(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marks_scored = models.IntegerField(default=0)
    time_started = models.DateTimeField(default=now)
