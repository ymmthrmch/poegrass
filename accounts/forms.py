from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'email',
            'account_id',
            'last_name',
            'first_name',
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'placeholder': "空欄可"}),
        }

class LoginForm(AuthenticationForm):
    class Meta:
        model = User