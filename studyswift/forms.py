from allauth.account.forms import SignupForm
from django import forms
from .models import UserProfile, Flashcard

class CustomSignupForm(SignupForm):
    is_teacher = forms.BooleanField(required=False)

    def save(self, request):
        user = super().save(request)
        profile = UserProfile.objects.create(user=user, is_teacher=self.cleaned_data['is_teacher'])
        return user

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ["subject", "question", "answer"]
        