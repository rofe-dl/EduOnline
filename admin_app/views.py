from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .models import *
from .forms import CreateExamDetailsForm, CreateSubjectForm

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

def redirect_if_user(function):
    """ A decorator applied over every function so that if a student/user tried to access the url of an admin,
    they get redirected """

    def _function(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse("user_app:index"))
        
        return function(request, *args, **kwargs)
    
    return _function


@login_required(login_url=login_url)
@redirect_if_user
def index(request):
    return HttpResponseRedirect(reverse("admin_app:exams"))

@login_required(login_url=login_url)
@redirect_if_user
def subjects_view(request):
    """ 
    Shows all the subjects available in the database.
    
    """
    return render(request, subjects_url,{
        "subjects" : Subject.objects.all()
    })

@login_required(login_url=login_url)
@redirect_if_user
def add_subject_view(request):
    """
    Adds a new subject to the database with the create subject form.
    Then redirects to the list of subjects.

    """
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
    """
    Deletes a subject and redirects to the list of subjects.

    Args:
        subject_name (str): The subject name of the subject to delete

    """
    query = Subject.objects.filter(subject_name=subject_name)
    query.delete()

    messages.success(request, "Subject deleted")
    return HttpResponseRedirect(reverse("admin_app:subjects"))

@login_required(login_url=login_url)
@redirect_if_user
def exams_view(request):

    exams = Exam.objects.all()
    exams_filter = ExamFilter(request.GET, queryset=exams)

    return render(request, exams_url,{
        "exams" : exams_filter
    })

@login_required(login_url=login_url)
@redirect_if_user
def toggle_exam_view(request, exam_id):
    """
    Method to call when admin makes an exam available or unavailable with the checkbox
    Checkbox sends a POST request with jQuery that is received by this method.
    Redirects to the list of exams

    Args:
        exam_id (str): Exam ID of the exam to toggle

    """
    if request.method == "POST":
        exam = Exam.objects.get(exam_id=exam_id)

        # if the check box is ticked, exam-toggle will be in post request, meaning make exam available
        if "exam-toggle" in request.POST:
            exam.available = True
        else:
            exam.available = False

        exam.save()

    return HttpResponseRedirect(reverse('admin_app:exams'))

"""
Creating exams is a two step process:
    1. Create the details of the exam, like name, duration, class etc.
    2. Creating the question paper of the exam
"""

@login_required(login_url=login_url)
@redirect_if_user
def create_exam_details_view(request):
    """
    Displays the form to create a new exam and redirects to the question paper making page

    """
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
    """
    Displays the question paper making page.
    If method is post, exam question is first created without its choices with add_question method
    If that's successful, the choices are added with the add_choices method

    Args:
        exam_id (str): Exam ID of the newly created exam to create questions for

    """
    exam = Exam.objects.get(exam_id=exam_id)
    
    # if admin submits a new question
    if request.method == "POST":
        # adds the question without its choices, returns true if succesfully added
        question = add_question(request, exam)

        # if question was created successfully
        if question: 
            # then adds the choices to the question, returns true if successfully added
            if add_choices(request, question):
                exam.total_marks = exam.total_marks + int(question.mark)
                exam.save()

    return render(request, create_exam_questions_url,{
        "exam_id" : exam_id,
        "exam_name" : exam.exam_name
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
                question.delete()
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
        return HttpResponseRedirect(reverse("admin_app:exams"))

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
        "exam_id" : exam_id,
        "exam_name" : exam.exam_name
    })

@login_required(login_url=login_url)
@redirect_if_user
def delete_exam_view(request, exam_id):
    """
    Deletes an exam from the database and redirects to list of exams

    Args:
        exam_id (str): Exam ID of the exam to delete
    
    """

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
        "users" : User.objects.filter(is_staff=False)
    })

@login_required(login_url=login_url)
@redirect_if_user
def remove_user_view(request, username):

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("admin_app:users"))

    if not user.is_staff:
        user.delete()

    return HttpResponseRedirect(reverse("admin_app:users"))


@login_required(login_url='/')
def edit_profile_view(request):
    profile_update_form = UserRegisterForm(instance=request.user)
     
    if request.method == 'POST':

        profile_update_form = UserRegisterForm(data=request.POST, instance=request.user)

        if profile_update_form.is_valid():

            user = profile_update_form.save() 
            update_session_auth_hash(request, user) # prevents logout by updating session
            messages.success(request, 'Profile Updated')

            return HttpResponseRedirect(reverse('admin_app:index'))

    return render(request, edit_profile_url,{
        'profile_update_form': profile_update_form
    })


""" HELPER METHODS """

def add_question(request, exam):
    """
    Adds a question to an exam
    Creates question object with solution_id not set because it's not known

    Args:
        exam (Exam): Exam object to add the question to

    Returns:
        question : Question object that is just created or false if not created

    """
    # generates unique id for exam
    question_id = "q-" + str(uuid.uuid4())

    # if question statement or mark is empty, return false
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
    """
    Adds the choices to the question

    Args:
        question (Question): Question object to add the choices to

    Returns:
        boolean : True if successfully added all choices with solution, false otherwise

    """
    
    # handles if user doesn't select any choice as a solution
    try:
        solution = request.POST["solution"]
    except KeyError:
        question.delete()
        return False

    # creates choice objects and set the solution id when a choice matches solution
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
    """
    Checks if a string is empty 
    """
    return not str(string.strip())