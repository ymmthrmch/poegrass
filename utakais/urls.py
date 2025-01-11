from . import views
from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import path

app_name = "utakais"

urlpatterns = [
    path('',views.EventIndexView.as_view()),
    path('<int:pk>/',views.change_event_view,name="event_detail"),
    path('create/',views.EventCreateView.as_view,name="event_create"),
    path('',views.EventIndexView.as_view(),name="events_index"),
]