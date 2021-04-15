from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout

index_html_dir = "user_auth/index.html"

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("admin_app:index"))

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('admin_app:index'))
        else:
            return render(request, index_html_dir, {
                "message" : "Username or Password is incorrect",
                "username" : username
            })
    
    return render(request, index_html_dir)

    