from pathlib import Path

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
)
from django.views.generic.edit import UpdateView

from .forms import EventForm, ParticipantForm, ParticipantFormSet, TankaForm
from .models import Event, Participant, Tanka


class EventIndexView(ListView):
    model = Event
    template_name = "utakais/events/index.html"
    context_object_name = "events"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_member:
            queryset = Event.objects.filter(ann_status__in=["public", "limited"])
        else:
            queryset = Event.objects.filter(ann_status="public")
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
    if event.ann_status == "public":
        if event.deadline > timezone.now():
            return EventDetailView.as_view()(request, pk=pk)
        else:
            return EventOngoingView.as_view()(request, pk=pk)
    elif event.ann_status == "limited":
        if user.is_authenticated and user.is_member:
            if event.deadline > timezone.now():
                return EventDetailView.as_view()(request, pk=pk)
            else:
                return EventOngoingView.as_view()(request, pk=pk)
        else:
            return event_not_found
    elif event.ann_status == "private":
        return event_not_found(request)


def event_not_found(request):
    return HttpResponseNotFound("<h1>歌会が見つかりません。</h1>")


class EventDetailView(FormView):
    template_name = "utakais/events/detail.html"
    form_class = ParticipantForm

    def form_invalid(self, form):
        tanka_form = TankaForm(self.request.POST)
        participant_form = ParticipantForm(self.request.POST)
        context = self.get_context_data(
            tanka_form=tanka_form,
            participant_form=participant_form,
        )
        return self.render_to_response(context)

    def form_valid(self, form):
        tanka_form = TankaForm(self.request.POST)
        participant_form = ParticipantForm(self.request.POST)
        user = self.request.user
        event = get_object_or_404(Event, pk=self.kwargs["pk"])

        if "delete" in self.request.POST:
            try:
                participant = Participant.objects.get(user=user, event=event)
                participant.delete()
                if participant.tanka:
                    participant.tanka.delete()
                messages.success(self.request, "参加を取り消しました。")
                return redirect("utakais:events_index")
            except Participant.DoesNotExist:
                messages.error(self.request, "参加の取り消しに失敗しました。")
                return self.request.path

        if tanka_form.is_valid() and participant_form.is_valid():
            empty = ""  # 詠草提出しない場合の詠草入力欄

            # ---tankaを保存---
            if not tanka_form.cleaned_data["content"] == empty:
                tanka = tanka_form.save(commit=False)
                tanka.author = user if user.is_authenticated else None
                tanka.save()
            else:
                tanka = None

            # ---Participantを保存---
            if user.is_authenticated:
                participant, created = Participant.objects.get_or_create(
                    user=user,
                    event=event,
                )

                if not created and participant.tanka:
                    participant.tanka.delete()

                participant.message = participant_form.cleaned_data["message"]
                messages.success(self.request, "再提出しました。")

            else:
                participant = participant_form.save(commit=False)
                participant.event = event
                participant.guest_user = tanka_form.cleaned_data["guest_author"]
                messages.success(self.request, "提出しました。")

            participant.tanka = tanka
            participant.save()

        else:
            messages.error(self.request, "提出に失敗しました。")
            return self.render_to_response(
                self.get_context_data(
                    tanka_form=tanka_form, participant_form=participant_form
                )
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        tanka_formとparticipant_formを設定
        ParticipantFormをログイン状態によって動的に変化させるため,userを渡す
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        context["event"] = event
        context["joined"] = False

        if "tanka_form" in kwargs and "participant_form" in kwargs:
            context["tanka_form"] = kwargs["tanka_form"]
            context["participant_form"] = kwargs["participant_form"]
            context["participant_form"].fields[
                "guest_user"
            ].widget = forms.HiddenInput()
            return context

        if user.is_authenticated:
            # ---tanka_formの初期値を設定---
            tanka_initial = {}
            try:
                participant = Participant.objects.get(user=user, event=event)
                context["joined"] = True
                if participant.tanka:
                    tanka_initial["content"] = participant.tanka.content
            except Participant.DoesNotExist:
                pass
            context["tanka_form"] = TankaForm(initial=tanka_initial, author=user)

            # ---participant_formの初期値,kwargsを設定---
            participant_initial = {}
            try:
                participant = Participant.objects.get(user=user, event=event)
                if participant.tanka:
                    participant_initial["message"] = participant.message
            except Participant.DoesNotExist:
                pass
            context["participant_form"] = ParticipantForm(
                initial=participant_initial,
                user=user,
            )

        else:
            context["tanka_form"] = TankaForm()
            context["participant_form"] = ParticipantForm(
                initial={
                    "guest_user": "未入力"
                },  # validationerrorを起こさないために仮置きしている。
                hide_guest_user=True,
            )

        return context

    def get_success_url(self):
        success_url = self.request.path
        return success_url


class EventCreateView(CreateView):
    model = Event
    template_name = "utakais/events/create.html"
    form_class = EventForm
    success_url = reverse_lazy("utakais:events_index")


class EventOngoingView(DetailView):
    model = Event
    template_name = "utakais/events/ongoing.html"

    def get(request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs["pk"])

        # サニタイズ（ファイル名の安全な形式への変換）された名前
        file_name = default_storage.get_valid_name(event.title)

        doc_path = settings.MEDIA_ROOT / Path(
            f"events/{event.pk}/{file_name}_ver{event.eisou_number}.docx"
        )
        pdf_path = settings.MEDIA_ROOT / Path(
            f"events/{event.pk}/{file_name}_ver{event.eisou_number}.pdf"
        )
        if doc_path.is_file() and pdf_path.is_file():
            pass
        else:
            event.generate_files()
        return super().get(request, *args, **kwargs)


class EventAdminView(UpdateView):
    model = Event
    fields = [
        "title",
        "start_time",
        "end_time",
        "location",
        "deadline",
        "ann_status",
        "ann_desc",
        "rec_status",
        "rec_desc",
        "eisou_doc",
        "eisou_pdf",
    ]
    template_name = "utakais/events/admin.html"

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event = self.get_object()
        context["event_form"] = self.get_form()

        if self.request.POST:
            context["participant_formset"] = ParticipantFormSet(
                self.request.POST, instance=event
            )
        else:
            context["participant_formset"] = ParticipantFormSet(instance=event)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        participant_formset: forms.BaseInlineFormSet = context["participant_formset"]

        self.object = form.save()
        participant_formset.save()

        return super().form_valid(form)


def download_eisou_file(request, pk, file_type):
    try:
        event = Event.objects.get(pk=pk)

        # file_typeに基づいて適切なFileFieldのパスを取得
        if hasattr(event, file_type):  # file_typeがモデルに存在するか確認
            file_field = getattr(event, file_type)
            if file_field:  # FileFieldが空でないか確認
                file_path = file_field.path
                return FileResponse(
                    open(file_path, "rb"), as_attachment=False, filename=file_field.name
                )
            else:
                raise FileNotFoundError("File field is empty.")
        else:
            raise AttributeError(f"{file_type} is not a valid file type for Event.")

    except Event.DoesNotExist:
        raise Http404("File does not exist")


def execute_method(request, pk, app_name, model_name, method_name):
    try:
        model = apps.get_model(app_name, model_name)
    except LookupError:
        raise ValueError(f"Model '{model_name}' not found.")
    obj = get_object_or_404(model, pk=pk)

    if not request.user.is_authenticated or request.user != obj.organizer:
        raise PermissionError("You are not allowed to execute this method.")

    if hasattr(obj, method_name):
        method = getattr(obj, method_name)

        if callable(method):
            method()  # 実行
        else:
            raise AttributeError(
                f"{method_name} is not a valid method for {obj.__class__.__name__}"
            )

    else:
        raise AttributeError(
            f"{method_name} is not a valid method for {obj.__class__.__name__}"
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


class TankaDetailView(FormView):
    model = Tanka
    template_name = "utakais/tankas/detail.html"
    form_class = TankaForm
