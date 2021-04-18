from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *

import uuid
# Create your views here.

# URL locations here, to centralize
login_url = '/'
index_url = 'admin_app/index.html'
subjects_url = 'admin_app/subjects.html'
add_subject_url = 'admin_app/add_subject.html'
exams_url = 'admin_app/exams.html'
create_exam_details_url = 'admin_app/create_exam_details.html'
create_exam_question_url = 'admin_app/create_exam_questions.html'

#TODO Prevent users from accessing administrator panel
#TODO Grey out submit button for question if no changes made
#TODO Update total marks of exam

@login_required(login_url=login_url)
def index(request):
    return render(request, index_url)

@login_required(login_url=login_url)
def subjects_view(request):
    return render(request, subjects_url,{
        "subjects" : Subject.objects.all()
    })

@login_required(login_url=login_url)
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

@login_required(login_url=login_url)
def delete_subject_view(request, subject_name):
    query = Subject.objects.filter(subject_name=subject_name)
    query.delete()

    return HttpResponseRedirect(reverse("admin_app:subjects"))

@login_required(login_url=login_url)
def exams_view(request):
    return render(request, exams_url,{
        "exams" : Exam.objects.filter(available=True)
    })

@login_required(login_url=login_url)
def create_exam_details_view(request):
    if(request.method == "POST"):
        exam_id = "e-" + str(uuid.uuid4()) #generates unique id for each exam
        exam = Exam(
            exam_id=exam_id,
            exam_name=request.POST["exam_name"],
            duration=request.POST["duration"],
            standard=request.POST["standard"],
            subject_name=Subject.objects.get(subject_name=request.POST["subject_name"]),
            admin=User.objects.get(username=request.user.username))
        exam.save()

        return HttpResponseRedirect(reverse("admin_app:create_exam_questions", kwargs={"exam_id":exam_id}))


    return render(request, create_exam_details_url,{
        "subjects" : Subject.objects.all()
    })

@login_required(login_url=login_url)
def create_exam_questions_view(request, exam_id):
    if(request.method == "POST"):
        solution = request.POST["solution"]
        choices = request.POST.getlist('choice')

        for choice in choices:
            

        question_id = "q-" + str(uuid.uuid4())
        question = Question(
            question_id=question_id,
            exam_id=exam_id,
            statement=request.POST["statement"],
            mark=int(request.POST["mark"]),
            solution_id=solution_id
        )
    return render(request, create_exam_question_url)

@login_required(login_url=login_url)
def delete_exam_view(request, exam_id):
    query = Exam.objects.filter(exam_id=exam_id)
    query.delete()

    return HttpResponseRedirect(reverse("admin_app:exams"))
    
# @login_required(login_url=login_url)
# def submit_question_view(request, exam_id):

