from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *

index_url = "user_auth/index.html"

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin_app:index'))

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if(user.profile.is_admin):
                return HttpResponseRedirect(reverse('admin_app:index'))
            else:
                return HttpResponseRedirect(reverse('user_app:index'))

        else:
            return render(request, index_url, {
                "login_message" : "Username or Password is incorrect",
                "login_username" : username
            })
    
    return render(request, index_url)

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if not password == confirm_password:
            return render(request, index_url, {
                "register_username" : username,
                "register_email" : email,
                "register_message" : "Passwords do not match"
            })

        elif User.objects.filter(username=username).exists():
            return render(request, index_url, {
                "register_username" : username,
                "register_email" : email,
                "register_message" : "Username already exists"
            })

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        profile = Profile(is_admin=False, user=user)
        profile.save()
        
        login(request, user)

        return HttpResponseRedirect(reverse('user_app:index'))

@login_required(login_url='/')
def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse('user_auth:index'))