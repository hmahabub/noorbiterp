from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .forms import LoginForm


class ERPLoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm


class ERPLogoutView(auth_views.LogoutView):
    pass


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
