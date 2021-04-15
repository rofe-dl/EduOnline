from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.
    
@login_required(login_url='/')
def index(request):
    return HttpResponse("Oh no")

@login_required(login_url='/')
def subjects_view(request):
    pass