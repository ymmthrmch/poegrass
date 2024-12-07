from . import views
from django.contrib import admin
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path('signup/',views.SignupView.as_view(),name="signup"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('logout/',views.LogoutView.as_view(),name="logout"),
    path('',views.IndexView.as_view(),name="index"),
]