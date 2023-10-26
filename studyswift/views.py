from django.shortcuts import get_object_or_404, redirect, render
from .models import Post
from django.utils import timezone
from .forms import PostForm

# Create your views here.
def index(request):
    return render(request, "login/index.html")


