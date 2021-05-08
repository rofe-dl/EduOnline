from django import forms
from .models import Exam, Subject

class CreateExamDetailsForm(forms.ModelForm):

    class Meta:
        model = Exam
        fields = ['exam_name', 'duration', 'standard', 'subject']
    
    def __init__(self, *args, **kwargs):
        super(CreateExamDetailsForm, self).__init__(*args, **kwargs)

        self.fields['exam_name'].label = "Exam Name"
        self.fields['standard'].label = "Class"
        self.fields['duration'].label = "Duration (mins)"

class CreateSubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['subject_name']

    def __init__(self, *args, **kwargs):
        super(CreateSubjectForm, self).__init__(*args, **kwargs)
        self.fields['subject_name'].label = "Subject Name"