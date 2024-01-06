from itertools import count
from django.shortcuts import get_object_or_404, redirect, render
from allauth.account.views import SignupView
from .forms import CustomSignupForm, FlashcardForm      
from .models import Flashcard, UserProfile
from django.db.models import Count 

def homepage(request):
    return render(request, "application/homepage.html")

class CustomSignupView(SignupView):
    form_class = CustomSignupForm


def dashboard(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            if profile.is_teacher:
                return render(request, "application/teacher_dashboard.html")
            else:
                return render(request, "application/dashboard.html")
        except UserProfile.DoesNotExist:
            return render(request, "application/dashboard.html")

    return render(request, "application/dashboard.html")

def self_rev(request):
    flashcards = Flashcard.objects.filter(owner=request.user)

    flashcard_data = flashcards.values('subject').annotate(count=Count('subject')).order_by('subject')
    
    flashcard_subjects = [data['subject'] for data in flashcard_data]
    flashcard_counts = [data['count'] for data in flashcard_data]

    chart_data = {
        'flashcard_subjects': flashcard_subjects,
        'flashcard_counts': flashcard_counts,
    }

    return render(request, 'flashcards/self_rev.html', {'chart_data': chart_data, 'flashcards': flashcards})

def create_flashcard(request):
    if request.method == "POST":
        form = FlashcardForm(request.POST)
        if form.is_valid():
            flashcard = form.save(commit=False)
            flashcard.owner = request.user
            flashcard.save()
            return redirect("revise_flashcard")
    else:
        form = FlashcardForm()
        print("creating form")
    return render(request, "flashcards/create_flashcard.html", {"form": form})

def revise_flashcard(request):
    flashcards = Flashcard.objects.filter(owner=request.user).order_by('subject')

    if request.method == 'POST':
        selected_flashcard_ids = request.POST.getlist('selected_flashcards')
        if 'delete' in request.POST and selected_flashcard_ids:
            Flashcard.objects.filter(id__in=selected_flashcard_ids).delete()
            flashcards = Flashcard.objects.order_by('subject')

        elif 'test' in request.POST and selected_flashcard_ids:
            flashcard_ids_str = ','.join(selected_flashcard_ids)
            return redirect('test_flashcard', flashcard_ids=flashcard_ids_str)
        
        elif "create" in request.POST:
            return redirect("create_flashcard")

    return render(request, 'flashcards/revise_flashcard.html', {'flashcards': flashcards})

def test_flashcard(request, flashcard_ids):
    flashcard_ids_list = [int(id) for id in flashcard_ids.split(',')]
    flashcards = Flashcard.objects.filter(id__in=flashcard_ids_list)

    score = None

    if request.method == "POST":
        # Ensure that the button name is 'check'
        if 'check' in request.POST:
            # Initialize variables for scoring
            total_questions = len(flashcards)
            correct_answers = 0

            # Iterate through each flashcard and check the entered answer
            for flashcard in flashcards:
                flashcard_id_str = str(flashcard.id)
                entered_answer = request.POST.get(f'answer_{flashcard_id_str}')

                # Compare the entered answer with the actual answer
                if entered_answer is not None and entered_answer.lower() == flashcard.answer.lower():
                    flashcard.correct = True
                    correct_answers += 1
                else:
                    flashcard.correct = False

            # Calculate the score
            score = f"{correct_answers}/{total_questions}"

    return render(request, 'flashcards/test_flashcard.html', {'flashcards': flashcards, 'score': score})

