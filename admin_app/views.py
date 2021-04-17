from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
# Create your views here.

# URL locations here, to centralize
index_url = 'admin_app/index.html'
subjects_url = 'admin_app/subjects.html'
add_subject_url = 'admin_app/add_subject.html'
exams_url = 'admin_app/exams.html'
add_exam_url = 'admin_app/add_exam.html'

@login_required(login_url='/')
def index(request):
    return render(request, index_url)

@login_required(login_url='/')
def subjects_view(request):
    return render(request, subjects_url,{
        "subjects" : Subject.objects.all()
    })

@login_required(login_url='/')
def add_subject_view(request):
    if(request.method == "POST"):
        subject_name = request.POST["subject_name"]

        if Subject.objects.filter(subject_name=subject_name).exists():
            return render(request, add_subject_url,{
                "message" : "Subject already exists!"
            })
        
        subject = Subject(subject_name=subject_name)
        subject.save()

        return HttpResponseRedirect(reverse("admin_app:subjects"))
    
    return render(request, add_subject_url)

@login_required(login_url='/')
def edit_subject_view(request):
    pass

@login_required(login_url='/')
def delete_subject_view(request, subject_name):
    query = Subject.objects.filter(subject_name=subject_name)
    query.delete()

    return HttpResponseRedirect(reverse("admin_app:subjects"))

@login_required(login_url='/')
def exams_view(request):
    return render(request, exams_url)

@login_required(login_url='/')
def add_exam_view(request):
    if(request.method == "POST"):
        pass

    return render(request, add_exam_url)

@login_required(login_url='/')
def delete_exam_view(request, exam_id):
    query = Exam.objects.filter(exam_id=exam_id)
    query.delete()

    return HttpResponseRedirect(reverse("admin_app:exams"))
    