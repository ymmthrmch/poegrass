from .models import User,Event,Tanka,Participant
from django import forms
from django.db import models

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'start_time',
            'end_time',
            'location',
            'deadline',
            'ann_desc',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '空欄の場合、開催日になります。'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'location':forms.TextInput(),
            'deadline':forms.DateTimeInput(attrs={'type':'datetime-local'}),
            'ann_desc':forms.Textarea(attrs={
                'rows': 5,
                'cols': 40,
                'placeholder': 'コメントを記入してください',
            }),
        }

class TankaForm(forms.ModelForm):
    class Meta:
        model = Tanka
        fields = [
            'content',
            'author',
            'guest_author',
        ]

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
            'user',
            'event',
            'tanka',
            'is_observer',
        ]