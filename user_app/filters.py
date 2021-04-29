from admin_app.models import Exam

import django_filters

class ExamFilter(django_filters.FilterSet):
    class Meta:
        model = Exam
        fields = ['exam_name', 'duration', 'standard', 'subject']