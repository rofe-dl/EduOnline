from django.shortcuts import render

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.template.defaulttags import register
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from admin_app.models import *

from user_app.models import *

from user_auth.forms import UserRegisterForm

from .filters import ExamFilter

# URL locations here, to centralize
login_url = "/"

index_url = "user_app/index.html"
exams_url = "user_app/exams.html"
give_exam_url = "user_app/give_exam.html"
report_card_url = "user_app/report_card.html"
edit_profile_url = "user_app/edit_profile.html"

#TODO recalculate marks for students if exam paper edited after they're done

def redirect_if_admin(function):
    """ A decorator applied over every function so that if an admin trie to access the url of a user,
    they get redirected to admin """

    def _function(request, *args, **kwargs):
        if request.user.is_staff:
            return HttpResponseRedirect(reverse("admin_app:index"))
        
        return function(request, *args, **kwargs)
    
    return _function

@login_required(login_url=login_url)
@redirect_if_admin
def index(request):
    return HttpResponseRedirect(reverse("user_app:exams"))

@login_required(login_url=login_url)
@redirect_if_admin
def exams_view(request):
    exams = Exam.objects.filter(available=True)
    exams_filter = ExamFilter(request.GET, queryset=exams)

    return render(request, exams_url,{
        "exams" : exams_filter
    })

@login_required(login_url=login_url)
@redirect_if_admin
def give_exam_view(request, exam_id, question_id=None):

    exam = Exam.objects.get(exam_id=exam_id)
    user = User.objects.get(username=request.user.username)
    
    # checks if user is currently giving another exam
    if ReportCard.objects.filter(user=user, is_ongoing=True).exclude(exam=exam).exists():
        messages.error(request, "You are already giving another exam!")
        return HttpResponseRedirect(reverse("user_app:exams"))

    # if user has not started this exam, make a new report card for it
    # else get the existing report card
    try:
        report_card = ReportCard.objects.get(exam=exam,user=user)
    except ReportCard.DoesNotExist:
        report_card = ReportCard(exam=exam, user=user)
        report_card.save()

    # checks if user has finished this exam before their time expired
    if not report_card.is_ongoing:
        messages.warning(request, "You have already given this exam")
        return HttpResponseRedirect(reverse("user_app:exams"))


    # checks if the user has enough time to still be giving the exam
    # by finding diff between time now and time started and comparing it against exam duration
    time_difference = now() - report_card.time_started
    if time_difference.total_seconds() >= exam.duration * 60:
        report_card.is_ongoing = False
        report_card.save()
        messages.info(request, "Your time is up!")
        return HttpResponseRedirect(reverse("user_app:exams"))
    

    # if user submits a question
    if request.method == "POST":
        question = Question.objects.get(question_id=question_id)
        
        # if current user has not submitted this question before
        if not SubmittedAnswer.objects.filter(user=user, question=question).exists():

            # if user manages to click submit without choosing an option, redirect them to exam page
            try:
                answer = Choice.objects.get(choice_id=request.POST["choice"])
            except KeyError:
                return HttpResponseRedirect(reverse("user_app:give_exam", kwargs={"exam_id" : exam.exam_id}))

            submitted_answer = SubmittedAnswer(
                user=user, 
                question=question,
                answer=answer
            )

            submitted_answer.save()

            # if user's answer is correct
            solution = Choice.objects.get(choice_id=question.solution_id)
            if request.POST["choice"] == solution.choice_id:
                report_card.marks_scored = report_card.marks_scored + question.mark
                report_card.save()
        
        return HttpResponseRedirect(reverse("user_app:exams"))
    
    # finds list of questions belonging to the exam with this exam id
    # and find submitted answers by this user
    questions = []
    submitted_answers = SubmittedAnswer.objects.filter(user=user)
    for question in Question.objects.filter(exam=exam):

        # marks a question as submitted if user has given it before so it's greyed out
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
            'submitted_answer_id' : submitted_answer.answer.choice_id if is_submitted else None
        })

    time_tuple = convert_time(int (exam.duration * 60 - time_difference.total_seconds()) )

    return render(request, give_exam_url, {
        "questions" : questions,
        "exam" : exam,
        "hours" : time_tuple[0],
        "mins" : time_tuple[1],
        "secs" : time_tuple[2]
    })

@login_required(login_url=login_url)
@redirect_if_admin
def end_exam_view(request, exam_id):
    exam = Exam.objects.get(exam_id=exam_id)
    user = User.objects.get(username=request.user.username)

    if request.method == "POST":
        try:
            report_card = ReportCard.objects.get(exam=exam,user=user)
        except ReportCard.DoesNotExist:
            report_card = ReportCard(exam=exam, user=user)
        
        report_card.is_ongoing = False
        report_card.save()
        messages.info(request, "Exam ended")
        return HttpResponseRedirect(reverse("user_app:exams"))


@login_required(login_url=login_url)
@redirect_if_admin
def report_card_view(request):
    user = User.objects.get(username=request.user.username)
    report_card, average_marks = get_user_report_card(user)

    return render(request, report_card_url, {
        "report_card" : report_card,
        "average_marks" : average_marks
    })

@login_required(login_url='/')
def edit_profile_view(request):
    profile_update_form = UserRegisterForm(instance=request.user)
    
    if request.method == 'POST':

        profile_update_form = UserRegisterForm(data=request.POST, instance=request.user)

        if profile_update_form.is_valid():

            user = profile_update_form.save() 
            update_session_auth_hash(request, user) # prevents logout by updating session
            messages.success(request, 'Profile Updated')

            return HttpResponseRedirect(reverse('user_app:index'))

    return render(request, edit_profile_url,{
        'profile_update_form': profile_update_form
    })

""" HELPER METHODS """

@register.filter
def get_item(dictionary, key):
    """ Method used in Django template to access a dictionary value by key """
    return dictionary.get(key)

def get_user_report_card(user):
    # Dictionary to keep track of exams given under a certain subject
    # Key : Subject, Value : List of dictionaries, each dictionary being an exam
    report_card = dict()
     
    # Dictionary to keep track of marks scored per subject
    scored_marks = dict()
    # Dictionary to keep track of total marks per subject
    total_marks = dict()

    for rc in ReportCard.objects.filter(user=user, is_ongoing=False):
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
        try:
            average_marks[subject] = round ((mark / total_marks[subject]) * 100)
        except ZeroDivisionError:
            average_marks[subject] = 0

    return report_card, average_marks

def convert_time(time):
    ''' Finds the time in hours, mins, secs given total seconds '''

    secs = time % 60
    mins = time // 60
    hours = mins // 60
    mins = mins % 60

    return (hours, mins, secs)