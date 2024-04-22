from typing import Any, Optional
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe


class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ""
        error_list = [
            f'<div class="error__item" style="margin-bottom: 5px;">{e}</div>'
            for e in self
        ]
        error_list_string = "".join(error_list)
        error_item_style = "font-family: monospace; font-style: italic; color: #c44a4a; text-align: center; margin-bottom: 5px;"
        return mark_safe(
            f'<div class="form__error-list" style="{error_item_style}">{error_list_string}</div>'
        )


class LoginUserForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs) -> None:
        kwargs_new = {"error_class": DivErrorList}
        kwargs_new.update(kwargs)
        super(self.__class__, self).__init__(*args, **kwargs_new)

    username = forms.CharField(
        label="login",
        widget=forms.TextInput(
            attrs={
                "class": "form__input",
                "type": "text",
                "placeholder": "Login or Email",
            }
        ),
    )

    password = forms.CharField(
        label="password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "Password",
            }
        ),
    )


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs) -> None:
        kwargs_new = {"error_class": DivErrorList}
        kwargs_new.update(kwargs)
        super(self.__class__, self).__init__(*args, **kwargs_new)

    username = forms.CharField(
        label="login",
        widget=forms.TextInput(
            attrs={
                "class": "form__input",
                "placeholder": "Login",
            }
        ),
    )

    email = forms.EmailField(
        label="email",
        widget=forms.EmailInput(
            attrs={
                "class": "form__input",
                "placeholder": "Email",
            }
        ),
    )

    password1 = forms.CharField(
        label="password1",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="password2",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "placeholder": "Repeat Password",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registred!")
        return email


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs_new = {"error_class": DivErrorList}
        kwargs_new.update(kwargs)
        super(self.__class__, self).__init__(*args, **kwargs_new)

    old_password = forms.CharField(
        label="Old password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "Old password",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "New password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Repeat new password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "Repeat new password",
            }
        ),
    )


class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs_new = {"error_class": DivErrorList}
        kwargs_new.update(kwargs)
        super(self.__class__, self).__init__(*args, **kwargs_new)

    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form__input", "placeholder": "Email"}),
    )


class UserPasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs_new = {"error_class": DivErrorList}
        kwargs_new.update(kwargs)
        super(self.__class__, self).__init__(*args, **kwargs_new)

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "New password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Repeat new password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "Repeat new password",
            }
        ),
    )
