from django.shortcuts import get_object_or_404, redirect, render
from allauth.account.views import SignupView
from .forms import CustomSignupForm, FlashcardForm, SchoolClassForm, JoinClassForm, UserProfileUpdateForm, HomeworkForm, HomeworkCompletionForm#, HomeworkSubmissionForm
from .models import Flashcard, UserProfile, SchoolClass, Reward, Homework, HomeworkFile#, HomeworkSubmission
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test



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
def manage_homework(request):
    profile = request.user.userprofile
    if profile.is_teacher:
        homeworks = Homework.objects.filter(teacher=request.user)
        return render(request, 'homework/manage_homework_teacher.html', {'homeworks': homeworks})
    else:
        missingHomeworks = []
        pendingHomeworks = []
        student_classes = request.user.classes_enrolled.all()
        completedHomeworks = Homework.objects.filter(submissions__completed=True, submissions__student=request.user)

        for student_class in student_classes:
            homework = Homework.objects.filter(assigned_class=student_class)
            for single_homework in homework:
                if single_homework not in completedHomeworks:
                    if single_homework.due_date < timezone.now():
                        missingHomeworks.append(single_homework)
                    else:
                        pendingHomeworks.append(single_homework)
                
        


        return render(request, 'homework/manage_homework.html', {'missingHomeworks': missingHomeworks, 'pendingHomeworks': pendingHomeworks, 'completedHomeworks': completedHomeworks})
    
@login_required
def create_homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.teacher = request.user
            homework.save()

            for file in request.FILES.getlist('files'):
                homework.files.create(file=file)

            form.save_m2m() 
            messages.success(request, 'Homework created successfully!')

            return redirect('manage_homework')  # Redirect to a view displaying all homework assignments
    else:
        form = HomeworkForm()

    return render(request, 'homework/create_homework.html', {'form': form, 'classes': SchoolClass.objects.all()})

@login_required
def edit_homework(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)

    if request.user != homework.teacher:
        return redirect('manage_homework')

    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES, instance=homework)
        if form.is_valid():

            new_homework = form.save(commit=False)

            if 'files' in request.FILES:
                for file in request.FILES.getlist('files'):
                    new_file = HomeworkFile(file=file)
                    new_file.save()
                    new_homework.files.add(new_file)
            
            new_homework.save()            
            form.save_m2m()  

            return redirect('manage_homework') 
    else:
        form = HomeworkForm(instance=homework)

    return render(request, 'homework/edit_homework.html', {'form': form, 'homework': homework})

@login_required
def remove_file(request, file_id, homework_id):
    file = get_object_or_404(HomeworkFile, id=file_id)
    file.delete()
    return redirect('edit_homework', homework_id=homework_id)

@login_required
def delete_homework(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)

    if request.user == homework.teacher:
        homework.delete()

    return redirect('manage_homework')

@login_required
def view_homework(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)
    teacher_files = homework.files.all()

    #submission = homework.submissions.filter(student=request.user).first()

    if request.method == 'POST':
        completion_form = HomeworkCompletionForm(request.POST, instance=request.user.student_submissions.filter(homework=homework).first())
        if completion_form.is_valid():
            submission = completion_form.save(commit=False)
            submission.homework = homework
            submission.student = request.user
            submission.save()
            messages.success(request, 'Homework marked as completed.')
            return redirect('view_homework', homework_id=homework_id)
    else:
        completion_form = HomeworkCompletionForm(instance=request.user.student_submissions.filter(homework=homework).first())

    #student_files = HomeworkSubmission.objects.filter(homework=homework, student=request.user)

    #if request.method == 'POST':
        #form = HomeworkSubmissionForm(request.POST, request.FILES, instance=homework)
        #if form.is_valid():
         #   new_submission = form.save(commit=False)
          #  new_submission.user = request.user
           # new_submission.homework = homework

            #if 'files' in request.FILES:
             #   for file in request.FILES.getlist('files'):
              #      new_file = HomeworkSubmission(file=file)
               #     new_file.save()
                #    new_submission.files.add(new_file)
            
            #new_submission.save()            
            #form.save_m2m()
        
        #completion = HomeworkCompletionForm(request.POST)
        #if completion.is_valid():
         #   completion.save()

          #  messages.success(request, 'Homework submitted successfully!')
           # return redirect('manage_homework')
    #else:
     #   form = HomeworkSubmissionForm(instance=homework)
        
    return render(request, 'homework/view_homework.html', {
        'homework': homework,
        'teacher_files': teacher_files,
        'completion_form': completion_form,
    })

###-------------------------------SETTINGS/PROFILE-------------------------------###
def update_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()

            messages.success(request, 'Your profile picture has been updated!')
            return redirect('update_profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        profile_form = UserProfileUpdateForm(instance=request.user.userprofile)
    
    if request.user.userprofile.is_teacher:
        return render(request, 'application/update_profile_teacher.html', {'profile_form': profile_form})
    else:
        return render(request, 'application/update_profile.html', {'profile_form': profile_form})