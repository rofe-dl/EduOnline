from django.urls import path

from . import views

app_name = 'admin_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('subjects/', views.subjects_view, name='subjects'),
    path('delete-subject/<str:subject_name>', views.delete_subject_view, name='delete_subject'),
    path('add-subject/', views.add_subject_view, name='add_subject'),
    path('exams/', views.exams_view, name='exams'),
    path('delete-exam/<str:exam_id>', views.delete_exam_view, name='delete_exam'),
    path('add-exam/', views.add_exam_view, name='add_exam')
]