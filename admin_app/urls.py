from django.urls import path

from . import views

app_name = 'admin_app'

urlpatterns = [
    path('', views.index, name='index'),

    path('edit-profile', views.edit_profile_view, name="edit_profile"),

    path('subjects/', views.subjects_view, name='subjects'),
    path('delete-subject/<str:subject_name>', views.delete_subject_view, name='delete_subject'),
    path('add-subject/', views.add_subject_view, name='add_subject'),

    path('exams/', views.exams_view, name='exams'),
    path('exams/toggle-exam/<str:exam_id>', views.toggle_exam_view, name="toggle_exam"),
    path('delete-exam/<str:exam_id>', views.delete_exam_view, name='delete_exam'),
    path('create-exam/details', views.create_exam_details_view, name='create_exam_details'),
    path('create-exam/<str:exam_id>/questions', views.create_exam_questions_view, name="create_exam_questions"),
    path('edit-exam/<str:exam_id>/details', views.edit_exam_details_view, name="edit_exam_details"),
    path('edit-exam/<str:exam_id>/questions', views.edit_exam_questions_view, name="edit_exam_questions"),
    
    path('edit-exam/<str:exam_id>/questions/<str:question_id>', views.edit_exam_questions_view, name="confirm_edit_exam_questions"),
    path('users', views.users_view, name="users"),
    path('report-card/<str:username>', views.report_card_view, name="report_card")
]