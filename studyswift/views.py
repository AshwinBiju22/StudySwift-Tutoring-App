from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import TimetableEntry

def timetable(request):
    timetable_entries = TimetableEntry.objects.all()
    return render(request, 'application/timetable.html', {'timetable_entries': timetable_entries})

def index(request):
    return render(request, "home/index.html")

def portal(request):
    return render(request, "login/portal.html")

def dashboard(request):
    return render(request, "application/dashboard.html")
