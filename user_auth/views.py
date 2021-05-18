from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .forms import UserRegisterForm

from .models import *

index_url = "user_auth/index.html"

def index(request):
    #checking if the user is authenticated
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin_app:index'))
    
    register_form = UserRegisterForm()
    login_form = AuthenticationForm()

    if request.method =='POST':

        login_form=AuthenticationForm(data=request.POST)
        
        if login_form.is_valid():

            #retrieves the user it found from the post request
            user=login_form.get_user()
            login(request, user)

            if user.is_staff:
                return HttpResponseRedirect(reverse('admin_app:index'))

            else:
                return HttpResponseRedirect(reverse('user_app:index'))    
                    

    #showing the empty forms
    return render(request, index_url,{
        'login_form':login_form,
        'register_form':register_form
    })

def register_view(request):
    
    if request.method == 'POST':

        register_form = UserRegisterForm(data=request.POST)

        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            
            return HttpResponseRedirect(reverse('user_app:index'))

    #if the form isnt valid
    return render(request, index_url,{

        #if the form isnt valid we take them to the homepage
        'login_form': AuthenticationForm(),
        'register_form': register_form

    })

@login_required(login_url='/')
def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse('user_auth:index'))