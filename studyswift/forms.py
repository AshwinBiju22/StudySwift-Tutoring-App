from allauth.account.forms import SignupForm
from django import forms
from .models import UserProfile, Flashcard, SchoolClass, Homework, HomeworkSubmission
from django.contrib.auth.models import User
from multiupload.fields import MultiFileField


class CustomSignupForm(SignupForm):
    is_teacher = forms.BooleanField(required=False)
    is_admin = forms.BooleanField(required=False)

    def save(self, request):
        user = super().save(request)
        profile = UserProfile.objects.create(user=user, is_teacher=self.cleaned_data['is_teacher'], is_admin=self.cleaned_data['is_admin'])
        return user

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ["subject", "question", "answer"]
        
class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name']

class JoinClassForm(forms.Form):
    code = forms.CharField(max_length=4)

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['good_points', 'bad_points']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

class HomeworkForm(forms.ModelForm):
    files = MultiFileField(min_num=1, max_num=5, max_file_size=1024 * 1024 * 5)

    class Meta:
        model = Homework
        fields = ['title', 'description', 'due_date', 'assigned_class']
        widgets = {
            'due_date': forms.TextInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['files'].required = False

#class HomeworkSubmissionForm(forms.ModelForm):
 #   files = MultiFileField(min_num=1, max_num=5, max_file_size=1024 * 1024 * 5)

#    class Meta:
 #       model = Homework
  #      fields = ['submissions']

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)

     #   self.fields['submissions'].required = False

class HomeworkCompletionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['completed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['completed'].required = False