from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'email',
            'account_id',
            'name',
        ]

class LoginForm(AuthenticationForm):
    class Meta:
        model = User