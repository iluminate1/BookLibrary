from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import LoginUserForm, RegisterUserForm


# Create your views here.
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "Users/profile.html"
    http_method_names = ["get"]
    login_url = "User:login"


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = "Users/login.html"
    extra_context = {"title": "Sing In"}

    def get_success_url(self):
        return reverse_lazy("home")


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "Users/registration.html"
    extra_context = {"title": "Sing Up"}
    success_url: str = reverse_lazy("User:profile")

    def form_valid(self, form: BaseModelForm) -> HttpResponse:

        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get("password1"))
        user.save()
        auth_user = authenticate(
            username=form.cleaned_data.get("username"),
            password=form.cleaned_data.get("password1"),
        )
        login(self.request, auth_user)

        return HttpResponseRedirect(self.success_url)
