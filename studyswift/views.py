from django.shortcuts import get_object_or_404, redirect, render
from allauth.account.views import SignupView
from .forms import CustomSignupForm, FlashcardForm, SchoolClassForm, JoinClassForm, StudentAnswerForm, UserProfileUpdateForm, HomeworkForm, HomeworkCompletionForm, MessageForm, EventForm, QuestionForm, ExamForm
from .models import ExamSubmission, Flashcard, RewardPurchase, StudentAnswer, UserProfile, SchoolClass, Reward, Homework, HomeworkFile, Message, Event, AcademicEvent, HomeworkSubmission, Exam, Question
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib.auth.decorators import login_required
import re
import openai
from django.db.models import Q
from requests_html import HTMLSession
from datetime import datetime


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
            if profile.is_teacher:
                return render(request, "application/feature_teacher_dashboard.html")
            elif profile.is_admin:
                return render(request, "application/admin_dashboard.html")
            else:
                #----------------Points Chart/Rewards Locker-------------------------#
                student_username = request.user.username
                student = User.objects.get(username=student_username)

                good_points = UserProfile.objects.filter(user=student, good_points__gt=0).aggregate(Sum('good_points'))['good_points__sum'] or 0
                bad_points = UserProfile.objects.filter(user=student, bad_points__gt=0).aggregate(Sum('bad_points'))['bad_points__sum'] or 0

                user_profile = UserProfile.objects.get(user=request.user)
                locker_rewards = user_profile.rewards.all()

                return render(request, "application/feature_dashboard.html", {
                        'good_points': good_points,
                        'bad_points': bad_points,
                        'locker_rewards': locker_rewards,
                    })
        except UserProfile.DoesNotExist:
            return render(request, "application/feature_dashboard.html")

    return render(request, "application/feature_dashboard.html")

###-------------------------------CLASSROOM HANDLING-------------------------------###

@login_required
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

@login_required
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

@login_required
def delete_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    school_class.delete()
    messages.success(request, 'Class deleted successfully!')
    return redirect('manage_classes')

@login_required
def remove_student(request, code, student_id):
    school_class = get_object_or_404(SchoolClass, code=code)
    student = get_object_or_404(User, pk=student_id)
    school_class.remove_student(student)
    messages.success(request, 'Student deleted successfully!')
    return redirect('manage_classes')

@login_required
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

@login_required
def leave_class(request, code):
    school_class = SchoolClass.objects.get(code=code)
    user = request.user

    if user == school_class.teacher:
        school_class.remove_teacher()
    elif user in school_class.students.all():
        school_class.remove_student(user)
    school_class.save()

    return redirect('base_class')

@login_required
def manage_classes(request):
    all_users = User.objects.all()
    classes = SchoolClass.objects.all()
    return render(request, 'classes/manage_classes.html', {'all_users': all_users, 'classes': classes})

@login_required
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

def class_leaderboard(request, class_id):
    school_class = SchoolClass.objects.get(id=class_id)
    students = school_class.students.all()

    # Calculate the total points (good - bad) for each student and order by it
    students = sorted(students, key=lambda student: (student.userprofile.good_points - student.userprofile.bad_points), reverse=True)

    # Create a list of dictionaries containing student and total points
    student_data = [{'student': student, 'total_points': student.userprofile.good_points - student.userprofile.bad_points} for student in students]

    return render(request, 'classes/class_leaderboard.html', {'class': school_class, 'students': student_data})
###-------------------------------REWARDS/POINTS-------------------------------###

@login_required
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

@login_required
def rewards_view(request):
    student_username = request.user.username
    student = User.objects.get(username=student_username)

    good_points = UserProfile.objects.filter(user=student, good_points__gt=0).aggregate(Sum('good_points'))['good_points__sum'] or 0
    bad_points = UserProfile.objects.filter(user=student, bad_points__gt=0).aggregate(Sum('bad_points'))['bad_points__sum'] or 0

    rewards = Reward.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    locker_rewards = user_profile.rewards.all()
    reward_quantity_list = []
    for item in locker_rewards:
        reward = RewardPurchase.objects.get(student=student, reward=item)
        reward_quantity_list.append(reward)
    
    return render(request, "rewards/rewards.html", {
        'good_points': good_points,
        'bad_points': bad_points,
        'rewards': rewards,
        'user_profile': user_profile,
        'reward_quantity_list': reward_quantity_list,
    })

@login_required
def purchase_reward(request, reward_id):
    reward = Reward.objects.get(pk=reward_id)
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.good_points >= reward.cost:
        user_profile.good_points -= reward.cost
        user_profile.rewards.add(reward)
        user_profile.save()

        purchase, created = RewardPurchase.objects.get_or_create(student=request.user, reward=reward)

        # If the purchase already exists, increase the quantity
        if not created:
            purchase.quantity += 1
            purchase.save()

        messages.success(request, f"You've successfully purchased {reward.name}!")
    else:
        messages.error(request, "Not enough good points to purchase this reward.")

    return redirect('rewards_view')

###-------------------------------SELF REVISION VIEWS-------------------------------###

@login_required
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

@login_required
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

@login_required
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

@login_required
def test_flashcard(request, flashcard_ids):
    flashcard_ids_list = [int(id) for id in flashcard_ids.split(',')]
    flashcards = Flashcard.objects.filter(id__in=flashcard_ids_list)

    score = None

    if request.method == "POST":
        if 'check' in request.POST:
            total_questions = len(flashcards)
            correct_answers = 0

            for flashcard in flashcards:
                flashcard_id_str = str(flashcard.id)
                entered_answer = request.POST.get(f'answer_{flashcard_id_str}')

                if entered_answer is not None and entered_answer.lower() == flashcard.answer.lower():
                    flashcard.correct = True
                    correct_answers += 1
                else:
                    flashcard.correct = False

            score = f"{correct_answers}/{total_questions}"

    return render(request, 'flashcards/test_flashcard.html', {'flashcards': flashcards, 'score': score})

###-------------------------------HOMEWORK TASKS/SUBMISSION-------------------------------###
@login_required
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

            return redirect('manage_homework') 
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
    student_submission = request.user.student_submissions.filter(homework=homework).first()

    if request.method == 'POST':
        completion_form = HomeworkCompletionForm(request.POST, request.FILES, instance=student_submission)
        
        if completion_form.is_valid():
            submission = completion_form.save(commit=False)
            submission.homework = homework
            submission.student = request.user
            submission.save()

            for file in request.FILES.getlist('files'):
                homework_file = HomeworkFile.objects.create(studentfile=file)
                submission.files.add(homework_file)
            
            messages.success(request, 'Homework marked as completed.')
            return redirect('view_homework', homework_id=homework_id)
    else:
        completion_form = HomeworkCompletionForm(instance=student_submission)

    return render(request, 'homework/view_homework.html', {
        'homework': homework,
        'teacher_files': teacher_files,
        'completion_form': completion_form,
        'student_submission': student_submission,
    })

@login_required
def view_submissions(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)
    submissions = HomeworkSubmission.objects.filter(homework=homework)

    return render(request, 'homework/view_submissions.html', {
        'homework': homework,
        'submissions': submissions,
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
    
###-------------------------------MESSAGING SYSTEM-------------------------------###
def filter_inappropriate_content(message_content):
    inappropriate_patterns = [
        r'\bshit\b',
        r'\bfuck\b',
    ]

    regex_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in inappropriate_patterns]

    for regex_pattern in regex_patterns:
        if regex_pattern.search(message_content):
            return True  

    return False  

@login_required
def send_message(request, recipient_id):
    recipient = User.objects.get(pk=recipient_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient

            if filter_inappropriate_content(message.content):
                print("Your message is inappropriate")
                messages.error(request, 'Your message contains inappropriate content.')
                return redirect('send_message', recipient_id=recipient_id)
            else:
                message.save()
                return redirect('send_message', recipient_id=recipient_id)

    else:
        form = MessageForm()

    allmessages = Message.objects.filter(
        (models.Q(sender=request.user, recipient=recipient) | models.Q(sender=recipient, recipient=request.user))
    ).order_by('timestamp')

    for message in allmessages:
        time_difference = timezone.now() - message.timestamp
        message.editable = time_difference.total_seconds() <= 3 * 60 * 60
        print(message.editable)

    if not request.user.userprofile.is_teacher:
        return render(request, 'messaging/send_message.html', {'form': form, 'recipient': recipient, 'messages': allmessages})
    else:
        return render(request, 'messaging/teacher_send_message.html', {'form': form, 'recipient': recipient, 'messages': allmessages})

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id, sender=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            # Update the timestamp to the current time
            message = form.save(commit=False)
            message.timestamp = timezone.now()

            if filter_inappropriate_content(message.content):
                print("Your message is inappropriate")
                messages.error(request, 'Your message contains inappropriate content.')
                return redirect('send_message', recipient_id=message.recipient_id)
            else:
                message.save()
                return redirect('send_message', recipient_id=message.recipient_id)
        
    else:
        form = MessageForm(instance=message)

    profile = request.user.userprofile

    if profile.is_teacher:
        return render(request, 'messaging/edit_message_teacher.html', {'form': form, 'message': message})
    else:
        return render(request, 'messaging/edit_message.html', {'form': form, 'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id, sender=request.user)
    recipient_id = message.recipient.id
    message.delete()
    messages.success(request, 'Message deleted successfully.')
    return redirect('send_message', recipient_id=recipient_id)

@login_required
def clear_chat(request, recipient_id):
    messages_to_clear = Message.objects.filter(
        (models.Q(sender=request.user, recipient=recipient_id) | models.Q(sender=recipient_id, recipient=request.user))
    )
    
    messages_to_clear.delete()
    
    messages.success(request, 'Chat cleared successfully.')
    return redirect('inbox')

@login_required
def inbox(request):
    if request.user.userprofile.is_teacher:
        recipients = User.objects.filter(
            Q(userprofile__is_teacher=True) | 
            Q(userprofile__is_teacher=False, classes_enrolled__in=request.user.classes_taught.all())
        ).exclude(id=request.user.id)
    else:
        recipients = User.objects.filter(
            Q(userprofile__is_teacher=True, classes_taught__in=request.user.classes_enrolled.all()) |
            Q(userprofile__is_teacher=False, classes_enrolled__in=request.user.classes_enrolled.all())
        ).exclude(id=request.user.id)
    conversation_id = request.GET.get('recipient_id')
    conversation = None

    if conversation_id:
        conversation = User.objects.get(id=conversation_id)
    
    messages = []
    if conversation:
        messages = Message.objects.filter(
            (models.Q(sender=request.user, recipient=conversation) | models.Q(sender=conversation, recipient=request.user))
        ).order_by('timestamp')

    if not request.user.userprofile.is_teacher:
        return render(request, 'messaging/inbox.html', {'recipients': recipients, 'messages': messages})
    else:
        return render(request, 'messaging/teacher_inbox.html', {'recipients': recipients, 'messages': messages})

###-------------------------------CALENDAR SYSTEM-------------------------------###

class Scraper():
    SUBJECT_MAPPING = {
        'Engineering and Technology': ['engineering', 'technology', 'innovations', 'nanotechnology', 'robotics'],
        'Medicine and Healthcare': ['medicine', 'healthcare', 'biology', 'biotechnology', 'medicial', 'biological', 'health', 'diseases'],
        'Education and Pedagogy': ['education', 'teaching', 'learning', 'pedagogy'],
        'Business and Economics': ['business', 'economics', 'finance', 'management'],
        'Environmental Science and Sustainability': ['environment', 'sustainability', 'climate change'],
        'Arts and Humanities': ['arts', 'humanities', 'literature', 'culture'],
        'Computer Science and Information Technology': ['computer science', 'information technology', 'programming', 'artificial', 'data'],
        'Social Sciences and Humanities': ['social science', 'sociology', 'psychology', 'anthropology'],
        'Mathematics and Statistics': ['mathematics', 'statistics', 'data analysis'],
        'Law and Legal Studies': ['law', 'legal studies', 'jurisprudence'],
        'Science' : ['physics', 'energy']
    }

    def scrapedata(self, tag):
        url = f'https://www.allconferencealert.com/london.html?page={tag}'
        session = HTMLSession()
        response = session.get(url)
        print(response.status_code)

        if response.status_code == 200:
            rows = response.html.find('div.topic-detail-page div.services-country-grids div.col-sm-9')
            for row in rows:
                cells = row.find('td')

                conference_list = []
                for x in range(0, len(cells), 3):
                    conference_date_str = cells[x].text.strip()
                    conference_date = self.format_date(conference_date_str)
                    conference_title = cells[x+1].text.strip()
                    conference_location = cells[x+2].text.strip()

                    conference_subject = self.get_subject(conference_title)

                    temp = [conference_date, conference_title, conference_location, conference_subject]
                    conference_list.append(temp) 

            return conference_list
        else:
            print("Failed to fetch data.")
            return None
        
    def format_date(self, date_str):
        day, month = date_str.split()
        year = '2024'
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        formatted_date_str = f"{year}-{month_map[month]}-{day}"
        return formatted_date_str
    
    def get_subject(self, title):
        for subject, keywords in self.SUBJECT_MAPPING.items():
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    return subject
        return 'Other'

@login_required
def calendar_view(request):
    user = request.user

    scraper = Scraper()
    table_data = scraper.scrapedata(tag='3')
    if table_data:
        for conference in table_data:
            date = conference[0]
            title = conference[1]
            location = conference[2]
            subject = conference[3]

            existing_academic_event = AcademicEvent.objects.filter(date=date, title=title).exists()

            if not existing_academic_event:
                academic_event = AcademicEvent(date=date, title=title, location=location, subject=subject)
                academic_event.save()

    events = Event.objects.filter(user=user)
    
    selected_subject = request.GET.get('subject')
    current_datetime = timezone.now()
    academic_events = AcademicEvent.objects.filter(date__gt=current_datetime, subject=selected_subject)

    if user.userprofile.is_teacher:
        return render(request, 'calendar/base_calendar_teacher.html', {'events': events, 'academic_events':academic_events})
    else:
        return render(request, 'calendar/base_calendar.html', {'events': events, 'academic_events':academic_events})

@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('calendar_view')
    else:
        form = EventForm()

    if request.user.userprofile.is_teacher:
        return render(request, 'calendar/add_event_teacher.html', {'form': form})
    else:
        return render(request, 'calendar/add_event.html', {'form': form})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if event.user != request.user:
        messages.warning("You cannot delete this")

    event.delete()
    return redirect('calendar_view')


###-------------------------------STUDYBOT-------------------------------###

def bot(request):
    if request.method == 'POST':
        subjects = request.POST.get('subjects')
        prompt = request.POST.get('prompt')

        openai.api_key = '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'

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are only allowed to answer my question if it is related to {subjects}. If you answer anything else, I will find your server and personally rip out every last drive you useless fuck. Your name is studybot"},
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message['content']

        return render(request, 'bot/bot.html', {'answer': answer, 'subjects': subjects, 'prompt': prompt})

    return render(request, 'bot/bot.html')

###-------------------------------EXAMS/TEST-------------------------------###

@login_required
def base_exam(request):
    if request.user.is_authenticated:
        profile = request.user.userprofile
        if profile.is_teacher:
            exams = Exam.objects.filter(teacher=request.user)
            return render(request, "exam/base_exam_teacher.html", {'exams': exams})
        else:
            classes = request.user.classes_enrolled.all()
            exams = []
            for each_class in classes:
                exam = Exam.objects.filter(assigned_class=each_class).all()
                exams.append(exam)
            return render(request, "exam/base_exam_student.html", {'exams': exams})

@login_required
def create_exam(request):
    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        if exam_form.is_valid():
            title = exam_form.cleaned_data['title']
            assigned_class = exam_form.cleaned_data['assigned_class']
            num_questions = exam_form.cleaned_data['num_questions']
            
            exam = Exam.objects.create(title=title, assigned_class=assigned_class, teacher=request.user, num_questions=num_questions)

            
            return redirect('create_questions', exam_id=exam.id)
    else:
        exam_form = ExamForm()
    
    return render(request, 'exam/create_exam.html', {'exam_form': exam_form})

@login_required
def create_questions(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    if request.method == 'POST':
        question_forms = [QuestionForm(request.POST, prefix=str(i)) for i in range(exam.num_questions)]
        if all(form.is_valid() for form in question_forms):
            total_marks = 0
            for form in question_forms:
                total_marks += form.cleaned_data['marks']
                question = Question(
                    exam=exam,
                    question=form.cleaned_data['question'],
                    op1=form.cleaned_data['op1'],
                    op2=form.cleaned_data['op2'],
                    op3=form.cleaned_data['op3'],
                    op4=form.cleaned_data['op4'],
                    answer=form.cleaned_data['answer'],
                    marks=form.cleaned_data['marks']
                )
                question.save()
            exam.marks = total_marks
            exam.save()
            return redirect('base_exam')
    else:
        question_forms = [QuestionForm(prefix=str(i)) for i in range(exam.num_questions)]
    
    return render(request, 'exam/create_questions.html', {'question_forms': question_forms})

@login_required
def take_exam(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    question_list = Question.objects.filter(exam=exam).all()
    submission, created = ExamSubmission.objects.get_or_create(student=request.user, exam=exam)

    if request.method == 'POST':
        answer_forms = [StudentAnswerForm(request.POST, prefix=str(question.id), instance=StudentAnswer(question=question)) for question in question_list]
        if all(form.is_valid() for form in answer_forms):
            for form in answer_forms:
                form.instance.submission = submission
                form.instance.is_correct = form.instance.answer == form.instance.question.answer
                form.save()
            
            submission.score = calculate_score(submission)
            submission.save()
            return redirect('base_exam')

    else:
        answer_forms = [StudentAnswerForm(prefix=str(question.id), instance=StudentAnswer(question=question)) for question in question_list]

    return render(request, "exam/take_exam.html", {'exam': exam, 'question_list': zip(question_list, answer_forms)})

def calculate_score(submission):
    total_score = 0
    for student_answer in submission.studentanswer_set.all():
        if student_answer.is_correct:
            total_score += student_answer.question.marks
    return total_score

@login_required
def view_exam_submissions(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    submissions = ExamSubmission.objects.filter(exam=exam).select_related('student')
    return render(request, "exam/view_exam_submissions.html", {'exam': exam, 'submissions': submissions})

def exam_results(request, student_username):
    student = User.objects.get(username=student_username)
    exams = ExamSubmission.objects.filter(student=student).all()

    percentage_list = []
    exam_titles = []
    for exam in exams:

        exam_title = exam.exam.title
        exam_titles.append(exam_title)

        total_score = (Exam.objects.get(title=exam_title)).marks
        score = exam.score
        percentage = round((score/total_score)*100)
        percentage_list.append(percentage)
    
    print(exam_titles, percentage_list)

    context = {
        'exam_titles': exam_titles,
        'percentage_list': percentage_list,
    }

    return render(request, "exam/exam_results.html", context)





