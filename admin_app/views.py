from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .models import *
from .forms import CreateExamDetailsForm, CreateSubjectForm

from user_auth.models import Profile
from user_auth.forms import UserRegisterForm

from user_app.views import get_user_report_card
from user_app.filters import ExamFilter

import uuid


# URL locations here, to centralize
login_url = '/'

index_url = 'admin_app/index.html'
subjects_url = 'admin_app/subjects.html'
add_subject_url = 'admin_app/add_subject.html'
exams_url = 'admin_app/exams.html'
create_exam_details_url = 'admin_app/create_exam_details.html'
create_exam_questions_url = 'admin_app/create_exam_questions.html'
edit_exam_details_url = 'admin_app/edit_exam_details.html'
edit_exam_questions_url = 'admin_app/edit_exam_questions.html'
users_url = 'admin_app/users.html'
report_card_url = 'admin_app/report_card.html'
edit_profile_url = 'admin_app/edit_profile.html'

#TODO Download jquery
#TODO trim input when taking making question
#TODO separate js into js file for both edit and create questions
#TODO grey out question submit if a choice isn't selected in give exam
#TODO give site wide messages
#TODO add else to if request method isn't post so after operations are not performed
#TODO clean up repeat code using include of django templates
#TODO division by 0 error if total marks 0
#TODO show status if exam is available in table, and uploader
#TODO make html resume exam, not give
#TODO grey out submit if not selected

def redirect_if_user(function):
    """ A decorator applied over every function so that if a student/user tried to access the url of an admin,
    they get redirected """

    def _function(request, *args, **kwargs):
        if not request.user.profile.is_admin:
            return HttpResponseRedirect(reverse("user_app:index"))
        
        return function(request, *args, **kwargs)
    
    return _function


@login_required(login_url=login_url)
@redirect_if_user
def index(request):
    return render(request, index_url)

@login_required(login_url=login_url)
@redirect_if_user
def subjects_view(request):
    return render(request, subjects_url,{
        "subjects" : Subject.objects.all()
    })

@login_required(login_url=login_url)
@redirect_if_user
def add_subject_view(request):
    form = CreateSubjectForm()
    if request.method == "POST":
        form = CreateSubjectForm(request.POST)

        if form.is_valid():

            form.save()
            messages.success(request, "Subject added")
            return HttpResponseRedirect(reverse("admin_app:subjects"))
    
    return render(request, add_subject_url, {
        "form" : form
    })

@login_required(login_url=login_url)
@redirect_if_user
def delete_subject_view(request, subject_name):
    query = Subject.objects.filter(subject_name=subject_name)
    query.delete()

    messages.success(request, "Subject deleted")
    return HttpResponseRedirect(reverse("admin_app:subjects"))

@login_required(login_url=login_url)
@redirect_if_user
def exams_view(request):
    exams = Exam.objects.filter(available=True)
    exams_filter = ExamFilter(request.GET, queryset=exams)

    return render(request, exams_url,{
        "exams" : exams_filter
    })

@login_required(login_url=login_url)
@redirect_if_user
def create_exam_details_view(request):
    form = CreateExamDetailsForm()

    if request.method == "POST":
        form = CreateExamDetailsForm(request.POST)

        if form.is_valid():
            exam = form.save(commit=False) #commit false as it won't let us add without exam id

            exam_id = "e-" + str(uuid.uuid4()) #generates unique id for each exam
            user = User.objects.get(username=request.user.username)

            exam.exam_id = exam_id
            exam.admin = user

            exam.save()

        messages.success(request, "Exam created. Create your question paper here.")
        return HttpResponseRedirect(reverse("admin_app:create_exam_questions", kwargs={"exam_id":exam_id}))

    return render(request, create_exam_details_url,{
        "form" : form
    })

@login_required(login_url=login_url)
@redirect_if_user
def create_exam_questions_view(request, exam_id):
    exam = Exam.objects.get(exam_id=exam_id)
    
    if request.method == "POST":
        question = add_question(request, exam)

        # if question was created successfully
        if question: 
            exam.total_marks = exam.total_marks + int(question.mark)
            exam.save()
            add_choices(request, question)

    return render(request, create_exam_questions_url,{
        "exam_id" : exam_id
    })

@login_required(login_url=login_url)
@redirect_if_user
def edit_exam_details_view(request, exam_id):
    exam = Exam.objects.get(exam_id=exam_id)
    form = CreateExamDetailsForm(instance=exam)

    if request.method == "POST":
        form = CreateExamDetailsForm(request.POST, instance=exam)

        if form.is_valid:
            form.save()

        messages.success(request, "Exam details edited")
        # if just the details are edited
        if "save_details" in request.POST:
            return HttpResponseRedirect(reverse("admin_app:exams"))
        # if details are edited and further questions will be edited
        elif "edit_questions" in request.POST:
            return HttpResponseRedirect(reverse("admin_app:edit_exam_questions", kwargs={"exam_id":exam_id}))

    return render(request, edit_exam_details_url, {
        "form" : form,
        "exam" : exam
    })

@login_required(login_url=login_url)
@redirect_if_user
def edit_exam_questions_view(request, exam_id, question_id=None):
    exam = Exam.objects.get(exam_id=exam_id)

    if request.method == "POST":
        question = Question.objects.get(question_id=question_id)
        exam.total_marks = exam.total_marks - int(question.mark)

        if "submit_question" in request.POST:

            # deletes all existing choices of this question
            Choice.objects.filter(question=question).delete()

            # if one of the fields are empty
            if is_empty(request.POST["statement"]) or is_empty(request.POST["mark"]):
                pass
            else:
                question.statement = request.POST["statement"]
                question.mark = int(request.POST["mark"])

                question.save()

                # if all the choices have been added successfully, add the mark back
                if add_choices(request, question):
                    exam.total_marks = exam.total_marks + int(question.mark)
            
        elif "remove_question" in request.POST:
            question.delete()

        exam.save()


    # finds list of questions belonging to the exam with this exam id
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

    return render(request, edit_exam_questions_url, {
        "questions" : questions,
        "exam_id" : exam_id
    })

@login_required(login_url=login_url)
@redirect_if_user
def delete_exam_view(request, exam_id):
    query = Exam.objects.filter(exam_id=exam_id)
    query.delete()

    messages.success(request, "Exam deleted")
    return HttpResponseRedirect(reverse("admin_app:exams"))

@login_required(login_url=login_url)
@redirect_if_user
def report_card_view(request, username):
    user = User.objects.get(username=username)
    report_card, average_marks = get_user_report_card(user)

    return render(request, report_card_url, {
        "report_card" : report_card,
        "average_marks" : average_marks,
        "user" : user
    })

@login_required(login_url=login_url)
@redirect_if_user
def users_view(request):
    return render(request, users_url, {
        "profiles" : Profile.objects.filter(is_admin=False)
    })

@login_required(login_url='/')
def edit_profile_view(request):
    register_form = UserRegisterForm(instance=request.user)
    
    if request.method == "POST":
        register_form = UserRegisterForm(request.POST, instance=request.user)

        if register_form.is_valid():
            user = register_form.save()
            update_session_auth_hash(request, user) # prevents logout by updating session
            messages.success(request, "Profile updated")
            return HttpResponseRedirect(reverse("admin_app:index"))
        
        
    return render(request, edit_profile_url, {
        "register_form" : register_form
    })


""" HELPER METHODS """

def add_question(request, exam):
    # creates question object with solution_id not set because it's not known
    question_id = "q-" + str(uuid.uuid4())

    # if question statement or mark is empty
    if is_empty(request.POST["statement"]) or is_empty(request.POST["mark"]):
        return False

    question = Question(
        question_id=question_id,
        exam=exam,
        statement=request.POST["statement"],
        mark=int(request.POST["mark"])
    )

    question.save()

    return question

def add_choices(request, question):
    
    # handles if user doesn't select any choice as a solution
    try:
        solution = request.POST["solution"]
    except KeyError:
        question.delete()
        return False

    # creates choice objects and set the solution id when choice id match solution id
    choices = request.POST.getlist('choice')
    solution_id = ""

    for choice in choices:

        # if a choice box is empty
        if is_empty(choice):
            continue

        choice_id = "c-" + str(uuid.uuid4())
        choice_model = Choice(
            choice_id=choice_id,
            answer=choice,
            question=question
        )

        choice_model.save()

        if(choice == solution):
            solution_id = choice_id

    
    if not solution_id:
        # if chosen solution does not match any choice (e.g user chose en empty choice as solution)
        question.delete()
        return False
    else:
        # adds the solution to the previous question object
        question.solution_id = solution_id
        question.save()

        return True

def is_empty(string):
    return not str(string.strip())