from typing import Optional
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)

from .forms import (
    LoginUserForm,
    RegisterUserForm,
    UserPasswordChangeForm,
    UserPasswordResetConfirmForm,
    UserPasswordResetForm,
)


# Create your views here.
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "Users/profile.html"
    http_method_names = ["get"]
    login_url = "User:login"


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = "Users/login.html"
    extra_context = {"title": "Sing In"}

    def get(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("User:profile"))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("User:profile")


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "Users/registration.html"
    extra_context = {"title": "Sing Up"}
    success_url: str = reverse_lazy("User:profile")

    def get(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("User:profile"))
        return super().get(request, *args, **kwargs)

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


class LogoutUserView(LoginRequiredMixin, LogoutView):
    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(
            reverse_lazy("User:login") + f"?next={reverse_lazy('User:profile')}"
        )  # ???


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "Users/change_password.html"
    extra_context = {"title": "Change Password"}
    success_url = reverse_lazy("User:password-change-done")


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "Users/password_done.html"
    extra_context = {
        "title": "Change Password",
        "message": "Password changed successfully!",
    }

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        referer: Optional[str] = request.META.get("HTTP_REFERER", None)
        if not referer:
            return HttpResponseRedirect(reverse_lazy("User:profile"))

        if not referer.endswith(str(reverse_lazy("User:password-change"))):
            return HttpResponseRedirect(reverse_lazy("User:profile"))

        return super().get(request, *args, **kwargs)


class UserPasswordResetView(PasswordResetView):
    form_class = UserPasswordResetForm
    template_name = "Users/reset_password.html"
    email_template_name = "Users/password_reset_email.html"
    success_url = reverse_lazy("User:password-reset-done")
    extra_context = {"title": "Reset password"}


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "Users/password_done.html"
    extra_context = {
        "title": "Reset password",
        "message": "Password reset",
        "extra_message": "We’ve emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly.",
    }

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        referer: Optional[str] = request.META.get("HTTP_REFERER", None)
        if not referer:
            return HttpResponseRedirect(reverse_lazy("User:profile"))

        if not referer.endswith(str(reverse_lazy("User:password-reset"))):
            return HttpResponseRedirect(reverse_lazy("User:profile"))

        return super().get(request, *args, **kwargs)


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = UserPasswordResetConfirmForm
    template_name = "Users/password_reset_confirm.html"
    success_url = reverse_lazy("User:password-reset-complete")
    extra_context = {"title": "Password reset confirm"}


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "Users/password_done.html"
    extra_context = {
        "title": "Reset password complete",
        "message": "Password reset complete",
        "extra_message": "Password reseted successfully",
    }

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        referer: Optional[str] = request.META.get("HTTP_REFERER", None)
        if not referer:
            return HttpResponseRedirect(reverse_lazy("User:profile"))

        return super().get(request, *args, **kwargs)
