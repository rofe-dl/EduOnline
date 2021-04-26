from django.shortcuts import render

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from admin_app.models import *

login_url = "/"

index_url = "user_app/index.html"
exams_url = "user_app/exams.html"
give_exam_url = "user_app/give_exam.html"

def redirect_if_admin(function):
    """ A decorator applied over every function so that if an admin to access the url of a user,
    they get redirected to admin """

    def _function(request, *args, **kwargs):
        if request.user.profile.is_admin:
            return HttpResponseRedirect(reverse("admin_app:index"))
        
        return function(request, *args, **kwargs)
    
    return _function

@login_required(login_url=login_url)
@redirect_if_admin
def index(request):
    return render(request, index_url,{
        "page_title" : request.user.username
    })

@login_required(login_url=login_url)
@redirect_if_admin
def exams_view(request):

    return render(request, exams_url,{
        "exams" : Exam.objects.filter(available=True)
    })

@login_required(login_url=login_url)
@redirect_if_admin
def give_exam_view(request, exam_id, question_id=None):

    # if user submits a question
    if request.method == "POST":
        question = Question.objects.get(question_id=question_id)
        user = User.objects.get(username=request.user.username)
        exam = Exam.objects.get(exam_id=exam_id)

        report_card = ReportCard.objects.filter(exam=exam,user=user)

        # if user has not given this exam, make a new report card for it
        if not report_card.exists():
            report_card = ReportCard(exam=exam, user=user)
            report_card.save()

        # if current user has not submitted this question before
        if not SubmittedQuestion.objects.filter(user=user, question=question).exists():
            submitted_question = SubmittedQuestion(user=user, question=question)
            submitted_question.save()

            solution = Choice.objects.get(choice_id=question.solution_id)

            # if user's answer is correct
            if request.POST["choice"] == solution.answer:
                report_card.marks_scored = report_card.marks_scored + question.mark
        

    # finds list of questions belonging to the exam with this exam id
    exam = Exam.objects.get(exam_id=exam_id)
    questions = []
    for question in Question.objects.filter(exam=exam):

        choices = Choice.objects.filter(question=question)
        # adds a dictionary to the array that contains the question details
        questions.append({
            'statement' : question.statement,
            'mark' : question.mark,
            'choices' : choices,
            'solution' : Choice.objects.get(choice_id=question.solution_id),
            'id' : question.question_id
        })

    return render(request, give_exam_url, {
        "questions" : questions,
        "exam" : exam
    })
