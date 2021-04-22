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
    path('create-exam/details', views.create_exam_details_view, name='create_exam_details'),
    path('create-exam/<str:exam_id>/questions', views.create_exam_questions_view, name="create_exam_questions"),
    path('edit-exam/<str:exam_id>/details', views.edit_exam_details_view, name="edit_exam_details"),
    path('edit-exam/<str:exam_id>/questions', views.edit_exam_questions_view, name="edit_exam_questions"),
    path('edit-exam/<str:exam_id>/questions/<str:question_id>', views.edit_exam_questions_view, name="confirm_edit_exam_questions")
]