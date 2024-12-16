from .models import Event
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

class EventIndexView(ListView):
    model = Event
    template_name= 'utakais/index.html'
    context_object_name = 'events'

    def get_queryset(self):
          user = self.request.user
          if user.is_authenticated and user.is_member:
            queryset = Event.objects.filter(ann_status__in=['public', 'limited'])
          else:
            queryset = Event.objects.filter(ann_status='public')
          return queryset
    
class EventDetailView(DetailView):
    model = Event
    template_name = 'utakais/detail.html'
    context_object_name = 'event'

    def get_object(self):
          user = self.request.user
          event = Event.objects.filter(pk = self.kwargs['pk']).first()
          if event and not (event.ann_is_public or (user.is_authenticated and user.is_member)):
            event = None
          return event
     


