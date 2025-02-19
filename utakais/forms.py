from .models import Event,Tanka,Participant
from django import forms
from django.forms import inlineformset_factory

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
        fields = ['author', 'content', 'guest_author',]
    
    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].widget = forms.HiddenInput()

        if author and author.is_authenticated:
            # ログイン時は ログイン情報からauthorを設定し, guest_authorを非表示
            self.fields['author'].initial = author
            self.fields['guest_author'].widget = forms.HiddenInput()
            self.fields['guest_author'].required = False

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['user', 'guest_user', 'guest_contact', 'message',]

    def __init__(self, *args, user=None, hide_guest_user=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        
        if user and user.is_authenticated:
            # ログイン時は ログイン情報からuserを設定し, guest_user, guest_contact を非表示
            self.fields['user'].initial = user
            self.fields['guest_user'].widget = forms.HiddenInput()
            self.fields['guest_contact'].widget = forms.HiddenInput()
            self.fields['guest_user'].required = False
            self.fields['guest_contact'].required = False

        if hide_guest_user == True:
            self.fields['guest_user'].widget = forms.HiddenInput()

ParticipantFormSet = inlineformset_factory(
    Event,  # 親モデル
    Participant,  # 子モデル
    fields=['guest_user'],  # 編集可能なフィールド
    extra=0,  # 新規追加の空フォーム数
    can_delete=True  # 削除チェックボックスを有効にする
)