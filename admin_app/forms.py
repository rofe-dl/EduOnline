from django import forms
from .models import Exam

class CreateExamDetailsForm(forms.ModelForm):

    class Meta:
        model = Exam
        fields = ['exam_name', 'duration', 'standard', 'subject']