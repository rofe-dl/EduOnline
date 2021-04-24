from django.shortcuts import render

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from admin_app.models import *

index_url = "user_app/index.html"
login_url = "/"

@login_required(login_url=login_url)
def index(request):
    return render(request, index_url)