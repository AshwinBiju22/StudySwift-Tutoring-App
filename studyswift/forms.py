from allauth.account.forms import SignupForm
from django import forms
from .models import UserProfile, Flashcard, SchoolClass
from django.contrib.auth.models import User

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
