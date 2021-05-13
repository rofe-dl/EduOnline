from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .forms import UserRegisterForm

from .models import *

index_url = "user_auth/index.html"

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin_app:index'))

    register_form = UserRegisterForm()
    login_form = AuthenticationForm()

    if request.method == "POST":
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():
            user = login_form.get_user()

            login(request, user)

            if(user.is_staff):
                return HttpResponseRedirect(reverse('admin_app:index'))
            else:
                return HttpResponseRedirect(reverse('user_app:index'))
    

    return render(request, index_url, {
        'register_form' : register_form,
        "login_form" : login_form
    })

def register_view(request):
    
    if request.method == "POST":
        register_form = UserRegisterForm(request.POST)

        if register_form.is_valid():
            user = register_form.save()
            
            login(request, user)

            return HttpResponseRedirect(reverse('user_app:index'))

    return render(request, index_url, {
        'register_form' : register_form,
        'login_form' : AuthenticationForm()
    })

@login_required(login_url='/')
def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse('user_auth:index'))