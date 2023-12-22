import logging
from django.shortcuts import get_object_or_404, redirect, render

from allauth.account.views import SignupView
from .forms import CustomSignupForm

class CustomSignupView(SignupView):
    form_class = CustomSignupForm
        
from .models import UserProfile

def dashboard(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            if profile.is_teacher:
                return render(request, 'application/teacher_dashboard.html')
            else:
                return render(request, 'application/dashboard.html')
        except UserProfile.DoesNotExist:
            # Handle the case where the user doesn't have a profile
            return render(request, 'application/dashboard.html')

    return render(request, 'application/dashboard.html')

#def teacher_dashboard(request):
 #   return render(request, 'application/teacher_dashboard.html')

def index(request):
    return render(request, "home/index.html")

def portal(request):
    return render(request, "login/portal.html")

