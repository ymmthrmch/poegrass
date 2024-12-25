from .forms import EventForm,ParticipantForm,TankaForm
from .models import Event,Participant,Tanka
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404,render
from django.urls import reverse,reverse_lazy
from django.views.generic import CreateView,DetailView, FormView, ListView

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
        context['submitted'] = Participant.objects.filter(
            user=user,
            event=event,
            tanka__isnull=False  # tankaがNoneでない場合
            ).exists()
        return context
    
    def post(self, request, *args, **kwargs):
        if 'form_submit' in request.POST:
            
        
    
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

    # def get_context_data(self, **kwargs):
    #     """
    #     contextにevent,has_joined,has_submitted_tankaを追加または更新。
    #     """
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     event = get_object_or_404(Event, pk=self.kwargs['pk'])

    #     participant = Participant.objects.filter(user=user, event=event).first() if user.is_authenticated else None
    #     context.update({
    #         'event': event,
    #         'has_joined': participant is not None,
    #         'has_submitted_tanka': participant and participant.tanka is not None,
    #     })
    #     return context

    # def form_valid(self, form):
    #     event = get_object_or_404(Event, pk=self.kwargs['pk'])
    #     user = self.request.user

    #     if 'form_submit' in self.request.POST:
    #         tankaform = TankaForm(self.request.POST)
    #         if tankaform.is_valid():
    #             tanka = tankaform.save(commit=False)
    #             tanka.author = user if user.is_authenticated else None
    #             tanka.save()

    #             participant, created = Participant.objects.get_or_create(
    #                 user=user if user.is_authenticated else None,
    #                 guest_user=tanka.guest_author,
    #                 event=event,
    #             )
    #             if not created:
    #                 participant.tanka = tanka
    #                 participant.save()

    #     elif 'form_joined' in self.request.POST:
    #         participantform = ParticipantForm(self.request.POST)
    #         if participantform.is_valid():
    #             participant, created = Participant.objects.get_or_create(
    #                 user=user if user.is_authenticated else None,
    #                 guest_user=participantform.guest_author,
    #                 event=event,
    #             )

    #     return super().form_valid(form)

class EventCreateView(CreateView):
    model = Event
    template_name = 'utakais/events/create.html'
    form_class = EventForm
    success_url = reverse_lazy('utakais:events_index')