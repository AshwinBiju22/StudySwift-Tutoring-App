from django.shortcuts import get_object_or_404, redirect, render
from allauth.account.views import SignupView
from .forms import CustomSignupForm, FlashcardForm, SchoolClassForm, JoinClassForm
from .models import Flashcard, UserProfile, SchoolClass
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.models import User


# PATH OF APP DIRECTORY C:\Users\ashwi\Documents\studyswift_app\studyswift\

###-------------------------------DASHBOARD/LOGIN-------------------------------###

def homepage(request):
    return render(request, "application/homepage.html")

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

def dashboard(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            user = request.user
            if profile.is_teacher:
                return render(request, "application/teacher_dashboard.html")
            elif profile.is_admin:
                return render(request, "application/admin_dashboard.html")
            else:
                return render(request, "application/dashboard.html")
        except UserProfile.DoesNotExist:
            return render(request, "application/dashboard.html")

    return render(request, "application/dashboard.html")

###-------------------------------CLASSES/HOMEWORK-------------------------------###

def base_class(request):
    if request.user.is_authenticated:
        profile = request.user.userprofile
        user = request.user
        if profile.is_teacher:
            classes = user.classes_taught.all()
            return render(request, "classes/teacher_base_class.html", {'classes': classes})
        else:
            classes = user.classes_enrolled.all()
            return render(request, "classes/student_base_class.html", {'classes': classes})

def create_class(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully!')
            return redirect('manage_classes')
    else:
        form = SchoolClassForm()
    return render(request, 'classes/create_class.html', {'form': form})

def join_class(request):
    if request.method == 'POST':
        form = JoinClassForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                school_class = SchoolClass.objects.get(code=code)
                if school_class.teacher == request.user or request.user in school_class.students.all():
                    messages.warning(request, 'You are already a member of this class.')
                else:
                    if not school_class.teacher:
                        school_class.teacher = request.user
                    else:
                        school_class.students.add(request.user)
                    school_class.save()
                    messages.success(request, 'Joined class successfully!')
            except SchoolClass.DoesNotExist:
                messages.error(request, 'Invalid class code. Please try again.')
            return redirect('base_class')
    else:
        form = JoinClassForm()
    return render(request, 'classes/join_class.html', {'form': form})

def manage_classes(request):
    all_users = User.objects.all()
    classes = SchoolClass.objects.all()
    return render(request, 'classes/manage_classes.html', {'all_users': all_users, 'classes': classes})

def admin_move_user(request, user_id, class_id, action):
    user = User.objects.get(id=user_id)
    school_class = SchoolClass.objects.get(id=class_id)

    if action == 'add':
        user_class = request.POST.get('user_class')
        if user_class == 'teacher':
            school_class.add_teacher(user)
        elif user_class == 'student':
            school_class.add_student(user)
        school_class.save()

    elif action == 'remove':
        user_class = request.POST.get('user_class')
        if user_class == 'teacher':
            school_class.remove_teacher()
        elif user_class == 'student':
            school_class.remove_student(user)
        school_class.save()

    return redirect('manage_classes')

def leave_class(request, code):
    school_class = SchoolClass.objects.get(code=code)
    user = request.user

    if user == school_class.teacher:
        school_class.remove_teacher()
    elif user in school_class.students.all():
        school_class.remove_student(user)
    school_class.save()

    return redirect('base_class')

###-------------------------------SELF REVISION VIEWS-------------------------------###

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

###-------------------------------ZOOM INTEGRATION-------------------------------###
