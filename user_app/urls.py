from django.urls import path

from . import views

app_name = 'user_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('exams', views.exams_view, name='exams'),
    path('give-exam/<str:exam_id>', views.give_exam_view, name="give_exam"),
    path('give-exam/<str:exam_id>/<str:question_id>', views.give_exam_view, name="submit_question")
]