from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AVATAR_CHOICES, Profile

class RegisterForm(UserCreationForm):
    avatar = forms.ChoiceField(
        choices=AVATAR_CHOICES,
        widget=forms.RadioSelect,
        label='Выберите аватар',
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'avatar']

    def save(self, commit=True):
        user = super().save(commit)
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.avatar = self.cleaned_data['avatar']
        if commit:
            profile.save()
        return user
