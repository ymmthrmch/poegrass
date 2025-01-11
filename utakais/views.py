from .forms import EventForm,ParticipantForm,TankaForm
from .models import Event,Participant,Tanka
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse,HttpResponseNotFound
from django.shortcuts import get_object_or_404,render
from django.urls import reverse,reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView,DetailView,FormView,ListView,TemplateView
from docx.shared import Pt
import json
from pathlib import Path
from poegrass.utils import japanese_strftime

class EventIndexView(ListView):
    model = Event
    template_name = 'utakais/events/index.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_member:
            queryset = Event.objects.filter(ann_status__in=['public', 'limited'])
        else:
            queryset = Event.objects.filter(ann_status='public')
        return queryset
    
def change_event_view(request, pk):
    """
    歌会の公開非公開などによって表示するビューを変える。
    告知公開前->何も表示しない
    告知公開中から締め切り前->短歌投稿フォーム(EventDetailView)
    締め切り後->締め切りましたor短歌一覧（EventOngoingView）
    記録公開後->記録用のビュー（EventRecordView）
    """
    event = get_object_or_404(Event, pk=pk)
    user = request.user
    if event.ann_status == 'public':
        if event.deadline > timezone.now():
            return EventDetailView.as_view()(request,pk=pk)
        else:
            return EventOngoingView.as_view()(request,pk=pk)
    elif event.ann_status == 'limited':
        if user.is_authenticated and user.is_member:
            if event.deadline > timezone.now():
                return EventDetailView.as_view()(request,pk=pk)
            else:
                return EventOngoingView.as_view()(request,pk=pk)
        else:
            return event_not_found
    elif event.ann_status == 'private':
        return event_not_found(request)

def event_not_found(request):
    return HttpResponseNotFound("<h1>歌会が見つかりません。</h1>")

class EventDetailView(FormView):
    model = Tanka
    template_name = 'utakais/events/detail.html'
    form_class = TankaForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['author'].widget = forms.HiddenInput()

        if self.request.user.is_authenticated:
            form.fields['guest_author'].widget = forms.HiddenInput()
        
        return form
    
    def get_context_data(self, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['event'] = event
        if user.is_authenticated:
            participant = Participant.objects.filter(user=user, event=event).first()
            context['participant'] = participant
            context['submitted_tanka'] = participant.tanka if participant else None
        return context
    
    def form_valid(self,form):
        """
        詠草に従って短歌を保存。参加者情報も同時に保存、もしくは更新。
        """
        user = self.request.user
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        tanka = form.save(commit=False)
        tanka.author = user if user.is_authenticated else None
        tanka.guest_author = form.cleaned_data['guest_author'] if not user.is_authenticated else ""
        tanka.save()

        participant,created = Participant.objects.get_or_create(
            user = user if user.is_authenticated else None,
            guest_user = tanka.guest_author if not user.is_authenticated else "",           
            event = event,
            is_observer = True if not user.is_authenticated else False,
            )
        if not created and participant.tanka:
            participant.tanka.delete()
        participant.tanka = tanka
        participant.save()
            
        return super().form_valid(form) 

    def get_initial(self):
        """
        フォームに初期値を設定。
        ログインしている場合、authorをuserにする。
        ユーザーが既に短歌を提出している場合、その内容をデフォルトで表示する。
        """
        initial = super().get_initial()
        user = self.request.user
        event = get_object_or_404(Event, pk=self.kwargs['pk'])

        if user.is_authenticated:
            initial['author'] = user
            try:
                participant = Participant.objects.get(user=user, event=event)
                if participant.tanka:
                    initial['content'] = participant.tanka
            except Participant.DoesNotExist:
                pass

        return initial
    
    def get_success_url(self):
        return self.request.path

class EventCreateView(CreateView):
    model = Event
    template_name = 'utakais/events/create.html'
    form_class = EventForm
    success_url = reverse_lazy('utakais:events_index')

class EventOngoingView(TemplateView):
    template_name = 'utakais/events/ongoing.html'

    def get(self):
        event = get_object_or_404(Event,pk=self.request.kwargs['pk'])
        doc_path = settings.MEDIA_ROOT / Path(f'events/{event.pk}/{event.title}.docx')
        pdf_path = settings.MEDIA_ROOT / Path(f'events/{event.pk}/{event.title}.pdf')
        if doc_path.is_file():
            pass
        else:            
            event.generate_doc()
        if pdf_path.is_file():
            pass
        else:            
            event.generate_pdf()
        return super().get()