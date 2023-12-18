from django.shortcuts import get_object_or_404, redirect, render

def index(request):
    return render(request, "home/index.html")

def portal(request):
    return render(request, "login/portal.html")

def dashboard(request):
    return render(request, "application/dashboard.html")
