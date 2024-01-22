from django.shortcuts import get_object_or_404, redirect, render
from allauth.account.views import SignupView
from .forms import CustomSignupForm, FlashcardForm, SchoolClassForm, JoinClassForm, HomeworkForm, HomeworkSubmissionForm
from .models import Flashcard, UserProfile, SchoolClass, Reward, Homework, HomeworkSubmission
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone



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

###-------------------------------CLASSROOM HANDLING-------------------------------###

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

def leave_class(request, code):
    school_class = SchoolClass.objects.get(code=code)
    user = request.user

    if user == school_class.teacher:
        school_class.remove_teacher()
    elif user in school_class.students.all():
        school_class.remove_student(user)
    school_class.save()

    return redirect('base_class')

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

###-------------------------------REWARDS/POINTS-------------------------------###
def give_points(request, student_username):
    student = User.objects.get(username=student_username)
    teacher = request.user
    good_points = request.POST.get('good_points', 0)
    bad_points = request.POST.get('bad_points', 0)
    action = request.POST.get('action')
    
    if teacher.userprofile.is_teacher:
        if action == 'give':
            student.userprofile.good_points += int(good_points)
            student.userprofile.bad_points += int(bad_points)

        elif action == 'remove':
            student.userprofile.good_points -= int(good_points)
            student.userprofile.bad_points -= int(bad_points)
        
        if (student.userprofile.good_points < 0):
            student.userprofile.good_points = 0
        if (student.userprofile.bad_points < 0):
            student.userprofile.bad_points = 0

        student.userprofile.save()
    
    return redirect('base_class')

def rewards_view(request):
    student_username = request.user.username
    student = User.objects.get(username=student_username)

    good_points = UserProfile.objects.filter(user=student, good_points__gt=0).aggregate(Sum('good_points'))['good_points__sum'] or 0
    bad_points = UserProfile.objects.filter(user=student, bad_points__gt=0).aggregate(Sum('bad_points'))['bad_points__sum'] or 0

    rewards = Reward.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    locker_rewards = user_profile.rewards.all()

    return render(request, "rewards/rewards.html", {
        'good_points': good_points,
        'bad_points': bad_points,
        'rewards': rewards,
        'user_profile': user_profile,
        'locker_rewards': locker_rewards,
    })

def purchase_reward(request, reward_id):
    reward = Reward.objects.get(pk=reward_id)
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.good_points >= reward.cost:
        user_profile.good_points -= reward.cost
        user_profile.rewards.add(reward)
        user_profile.save()

        messages.success(request, f"You've successfully purchased {reward.name}!")
    else:
        messages.error(request, "Not enough good points to purchase this reward.")

    return redirect('rewards_view')

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

###-------------------------------HOMEWORK TASKS/SUBMISSION-------------------------------###
def create_homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.teacher = request.user
            homework.save()

            for file in request.FILES.getlist('files'):
                homework.files.create(file=file)

            form.save_m2m()  # Save many-to-many relationships, e.g., files
            messages.success(request, 'Homework created successfully!')
            return redirect('manage_homework')
    else:
        form = HomeworkForm()

    return render(request, 'homework/create_homework.html', {'form': form})

def manage_homework(request):
    if request.user.userprofile.is_teacher:
        # Teacher view
        homework_list = Homework.objects.filter(teacher=request.user)
        return render(request, 'homework/manage_homework_teacher.html', {'homework_list': homework_list})
    else:
        # Student view
        enrolled_classes = request.user.classes_enrolled.all()
        class_homework = []
        for student_class in enrolled_classes:
            homework_assignment = Homework.objects.filter(class_assigned=student_class)
            class_homework.extend(homework_assignment)
        submissions = HomeworkSubmission.objects.filter(student=request.user)
        return render(request, 'homework/manage_homework_student.html', {'submissions': submissions, 'class_homework':class_homework})

def view_homework(request, homework_id):
    homework = Homework.objects.get(pk=homework_id)
    
    # Ensure that only students who are assigned to the class can view the homework
    if (not request.user.userprofile.is_teacher and request.user not in homework.class_assigned.students.all()) or (request.user.userprofile.is_teacher):
        messages.error(request, 'You do not have permission to view this homework.')
        return redirect('manage_homework')
    else:
        try:
            submission = HomeworkSubmission.objects.get(homework=homework, student=request.user)
        except HomeworkSubmission.DoesNotExist:
            submission = None

        form = HomeworkSubmissionForm(instance=submission)

        if request.method == 'POST':
            form = HomeworkSubmissionForm(request.POST, request.FILES, instance=submission)
            
            if form.is_valid():
                submission = form.save(commit=False)
                submission.student = request.user
                submission.homework = homework
                submission.submitted = True  # Set submitted status to True
                submission.save()

                for file in request.FILES.getlist('files'):
                    submission.files.create(file=file)

                messages.success(request, 'Homework submitted successfully!')
                return redirect('view_homework', homework_id=homework_id)

    return render(request, 'homework/view_homework.html', {'homework': homework, 'submission': submission, 'form': form})

def complete_homework(request, submission_id):
    submission = HomeworkSubmission.objects.get(pk=submission_id)
    if submission.student == request.user:
        value = request.POST.get('status')
        if value == 'complete':
            submission.completed = True
            submission.completed_at = timezone.now()
            submission.submitted = True
            submission.save()
            messages.success(request, 'Homework marked as complete!')
        if value == 'incomplete':
            submission.completed = False  # Set completed status to False
            submission.completed_at = None
            submission.submitted = False  
            submission.save()
            messages.success(request, 'Homework marked as incomplete.')
        return redirect('view_homework', homework_id=submission.homework.id)
    else:
        messages.error(request, 'You do not have permission to complete this homework.')
        return redirect('manage_homework')

def homework_tasks(request):
    return render(request, "homework/homework_tasks.html") 