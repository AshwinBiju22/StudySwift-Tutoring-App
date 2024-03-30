from allauth.account.forms import SignupForm
from django import forms
from .models import (
    StudentAnswer,
    UserProfile,
    Flashcard,
    SchoolClass,
    Homework,
    HomeworkSubmission,
    Message,
    Event,
    Exam,
    Question,
    ExamSubmission,
)
from django.contrib.auth.models import User
from multiupload.fields import MultiFileField


class CustomSignupForm(SignupForm):
    is_teacher = forms.BooleanField(required=False)
    is_admin = forms.BooleanField(required=False)

    def save(self, request):
        user = super().save(request)
        profile = UserProfile.objects.create(
            user=user,
            is_teacher=self.cleaned_data["is_teacher"],
            is_admin=self.cleaned_data["is_admin"],
        )
        return user


class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ["subject", "question", "answer"]


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name"]


class JoinClassForm(forms.Form):
    code = forms.CharField(max_length=4)


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ["good_points", "bad_points"]


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]


class HomeworkForm(forms.ModelForm):
    files = MultiFileField(min_num=1, max_num=5, max_file_size=1024 * 1024 * 5)

    class Meta:
        model = Homework
        fields = ["title", "description", "due_date", "assigned_class"]
        widgets = {
            "due_date": forms.TextInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["files"].required = False


class HomeworkCompletionForm(forms.ModelForm):
    files = MultiFileField(
        min_num=0, max_num=5, max_file_size=1024 * 1024 * 5, required=False
    )

    class Meta:
        model = HomeworkSubmission
        fields = ["completed"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["completed"].required = False


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "start_datetime", "end_datetime"]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ExamForm(forms.Form):
    title = forms.CharField(max_length=100)
    assigned_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all())
    num_questions = forms.IntegerField(min_value=1, label="Number of Questions")


class QuestionForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea)
    op1 = forms.CharField(label="Option 1")
    op2 = forms.CharField(label="Option 2")
    op3 = forms.CharField(label="Option 3")
    op4 = forms.CharField(label="Option 4")
    answer = forms.ChoiceField(
        choices=[
            ("1", "Option 1"),
            ("2", "Option 2"),
            ("3", "Option 3"),
            ("4", "Option 4"),
        ]
    )
    marks = forms.IntegerField(min_value=1)


class StudentAnswerForm(forms.ModelForm):
    answer = forms.ChoiceField(
        choices=[
            ("1", "Option 1"),
            ("2", "Option 2"),
            ("3", "Option 3"),
            ("4", "Option 4"),
        ],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = StudentAnswer
        fields = ["answer"]
