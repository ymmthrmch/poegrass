from .forms import LoginForm,SignupForm
from django.contrib.auth import authenticate,login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView,TemplateView

class IndexView(LoginRequiredMixin,TemplateView):
     template_name = 'accounts/index.html'

class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        account_id = form.cleaned_data.get('account_id')
        password = form.cleaned_data.get('password1')
        user = authenticate(account_id=account_id, password=password)
        login(self.request, user)
        return response
    
    def get_success_url(self):
        next_url = self.request.GET.get("next")
        return next_url if next_url else reverse_lazy("{% url 'home' %}")
    
class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

class LogoutView(BaseLogoutView):
    success_url = reverse_lazy("index")