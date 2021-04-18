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
create_exam_questions_url = 'admin_app/create_exam_questions.html'
edit_exam_details_url = 'admin_app/edit_exam_details.html'

#TODO Prevent users from accessing administrator panel
#TODO Grey out submit button for question if no changes made
#TODO Update total marks of exam upon addition and deletion of question
#TODO Download jquery

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
    if request.method == "POST":
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
    if request.method == "POST":
        exam_id = "e-" + str(uuid.uuid4()) #generates unique id for each exam
        exam = Exam(
            exam_id=exam_id,
            exam_name=request.POST["exam_name"],
            duration=request.POST["duration"],
            standard=request.POST["standard"],
            subject=Subject.objects.get(subject_name=request.POST["subject_name"]),
            admin=User.objects.get(username=request.user.username))
        exam.save()

        return HttpResponseRedirect(reverse("admin_app:create_exam_questions", kwargs={"exam_id":exam_id}))

    return render(request, create_exam_details_url,{
        "subjects" : Subject.objects.all()
    })

@login_required(login_url=login_url)
def create_exam_questions_view(request, exam_id):
    if request.method == "POST":

        question_id = "q-" + str(uuid.uuid4())
        question = Question(
            question_id=question_id,
            exam=Exam.objects.get(exam_id=exam_id),
            statement=request.POST["statement"],
            mark=int(request.POST["marks"])
        )
        question.save()
        
        solution = request.POST["solution"]
        choices = request.POST.getlist('choice')

        for choice in choices:
            choice_id = "c-" + str(uuid.uuid4())
            choice_model = Choice(
                choice_id=choice_id,
                answer=choice,
                question=Question.objects.get(question_id=question_id)
            )

            choice_model.save()

            if(choice == solution):
                solution_id = choice_id


        setattr(question, "solution_id", solution_id)
        question.save()

    return render(request, create_exam_questions_url,{
        "exam_id" : exam_id
    })

@login_required(login_url=login_url)
def delete_exam_view(request, exam_id):
    query = Exam.objects.filter(exam_id=exam_id)
    query.delete()

    return HttpResponseRedirect(reverse("admin_app:exams"))

@login_required(login_url=login_url)
def edit_exam_details_view(request, exam_id):
    if request.method == "POST":
        pass

    exam = Exam.objects.get(exam_id=exam_id)
    return render(request, edit_exam_details_url, {
        "exam" : exam,
        "subjects" : Subject.objects.all()
    })

@login_required(login_url=login_url)
def edit_exam_questions_view(request, exam_id):
    pass