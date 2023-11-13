from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# Create your views here.
def index(request):
    return render(request, "home/index.html")

def signup(request):
    return render(request, "login/signup.html")

def signin(request):
    return render(request, "login/signin.html")

def portal(request):
    return render(request, "login/portal.html")

def menu(request):
    return render(request, "application/menu.html")

