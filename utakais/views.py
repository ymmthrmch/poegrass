from .models import Event
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView,TemplateView

class IndexView(LoginRequiredMixin,ListView):
    model = Event
    template_name= 'utakais/index.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(ann_status = 'public').order_by('-start_time')
