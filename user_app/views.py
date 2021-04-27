from django.shortcuts import render

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.template.defaulttags import register

from admin_app.models import *
from user_app.models import *

login_url = "/"

index_url = "user_app/index.html"
exams_url = "user_app/exams.html"
give_exam_url = "user_app/give_exam.html"
report_card_url = "user_app/report_card.html"

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
    return render(request, index_url)

@login_required(login_url=login_url)
@redirect_if_admin
def exams_view(request):

    return render(request, exams_url,{
        "exams" : Exam.objects.filter(available=True)
    })

@login_required(login_url=login_url)
@redirect_if_admin
def give_exam_view(request, exam_id, question_id=None):
    exam = Exam.objects.get(exam_id=exam_id)
    user = User.objects.get(username=request.user.username)

    report_card = ReportCard.objects.filter(exam=exam,user=user)

    # if user has not given this exam, make a new report card for it
    if not report_card.exists():
        report_card = ReportCard(exam=exam, user=user)
        report_card.save()
    else:
        report_card = ReportCard.objects.get(exam=exam,user=user)
        time_difference = now() - report_card.time_started

        if time_difference.total_seconds() >= exam.duration * 60:
            return HttpResponseRedirect(reverse("user_app:exams"))

    # if user submits a question
    if request.method == "POST":
        question = Question.objects.get(question_id=question_id)
        
        # if current user has not submitted this question before
        if not SubmittedAnswer.objects.filter(user=user, question=question).exists():
            submitted_answer = SubmittedAnswer(
                user=user, 
                question=question,
                submitted_answer=Choice.objects.get(choice_id=request.POST["choice"])
            )

            submitted_answer.save()
            solution = Choice.objects.get(choice_id=question.solution_id)

            # if user's answer is correct
            if request.POST["choice"] == solution.choice_id:
                report_card.marks_scored = report_card.marks_scored + question.mark
                report_card.save()
        
    submitted_answers = SubmittedAnswer.objects.filter(user=user)

    # finds list of questions belonging to the exam with this exam id
    questions = []
    for question in Question.objects.filter(exam=exam):
        try:
            submitted_answer = submitted_answers.get(question=question)
            is_submitted = True
        except SubmittedAnswer.DoesNotExist:
            submitted_answer = None
            is_submitted = False

        choices = Choice.objects.filter(question=question)

        # adds a dictionary to the array that contains the question details
        questions.append({
            'statement' : question.statement,
            'mark' : question.mark,
            'choices' : choices,
            'solution' : Choice.objects.get(choice_id=question.solution_id),
            'id' : question.question_id,
            'is_submitted' : is_submitted,
            'submitted_answer_id' : submitted_answer.submitted_answer.choice_id if is_submitted else None
        })

    return render(request, give_exam_url, {
        "questions" : questions,
        "exam" : exam
    })

@login_required(login_url=login_url)
@redirect_if_admin
def report_card_view(request):
    user = User.objects.get(username=request.user.username)
    report_card, average_marks = get_user_report_card(user)

    return render(request, report_card_url, {
        "report_card" : report_card,
        "average_marks" : average_marks
    })

def get_user_report_card(user):
    # Dictionary to keep track of exams given under a certain subject
    # Key : Subject, Value : List of dictionaries, each dictionary being an exam
    report_card = dict()
     
    # Dictionary to keep track of marks scored per subject
    scored_marks = dict()
    # Dictionary to keep track of total marks per subject
    total_marks = dict()

    for rc in ReportCard.objects.filter(user=user):
        subject = rc.exam.subject

        if not subject in report_card:
            report_card[subject] = []
            scored_marks[subject] = 0
            total_marks[subject] = 0
        
        num_of_exams = len(report_card[subject])

        report_card[subject].append({
            "marks_scored" : rc.marks_scored,
            "exam_name" : rc.exam.exam_name,
            "total_marks" : rc.exam.total_marks
        })
        
        total_marks[subject] = total_marks[subject] + rc.exam.total_marks
        scored_marks[subject] = scored_marks[subject] + rc.marks_scored
    
    # Calculates the average marks of each subject
    average_marks = dict()
    for subject, mark in scored_marks.items():
        average_marks[subject] = (mark / total_marks[subject]) * 100

    return report_card, average_marks

@register.filter
def get_item(dictionary, key):
    """ Method used in Django template to access a dictionary value by key """
    return dictionary.get(key)