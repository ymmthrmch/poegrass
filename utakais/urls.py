from . import views
from django.contrib import admin
from django.urls import path

app_name = "utakais"

urlpatterns = [
    path('',views.EventIndexView.as_view(),name="event_index"),
    path('<int:pk>/',views.EventDetailView.as_view(),name='event_detail'),
]