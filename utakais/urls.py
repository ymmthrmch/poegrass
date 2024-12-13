from . import views
from django.contrib import admin
from django.urls import path

app_name = "utakais"

urlpatterns = [
    path('',views.IndexView.as_view(),name="index"),
]