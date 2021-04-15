from django.urls import path

from . import views

app_name = 'admin_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('subjects/', views.subjects_view, name='subjects'),
    path('delete_subject/<str:subject_name>', views.delete_subject_view, name='delete_subject'),
    path('add_subject/', views.add_subject_view, name='add_subject')
]