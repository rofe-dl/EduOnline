from admin_app.models import Exam

import django_filters

class ExamFilter(django_filters.FilterSet):
    class Meta:
        model = Exam
        fields = ['exam_name', 'duration', 'standard', 'subject']
    
    def __init__(self, *args, **kwargs):
       super(ExamFilter, self).__init__(*args, **kwargs)
       self.filters['standard'].label = "Class"
       self.filters['exam_name'].label = "Exam Name"