from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import User


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


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "birthday",
            "sex",
            "city",
            "postcode",
            "background_cover",
            "photo",
            "is_visible",
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs_new = {"error_class": DivErrorList}
        kwargs_new.update(kwargs)
        super(self.__class__, self).__init__(*args, **kwargs_new)

    first_name = forms.CharField(
        label="First Name:",
        widget=forms.TextInput(
            attrs={
                "class": "text-field__input",
                "placeholder": "First Name",
            }
        ),
    )

    last_name = forms.CharField(
        label="Last Name:",
        widget=forms.TextInput(
            attrs={
                "class": "text-field__input",
                "placeholder": "Last Name",
            }
        ),
    )

    phone = forms.CharField(
        label="Phone Number:",
        widget=forms.TextInput(
            attrs={
                "class": "text-field__input",
                "placeholder": "+375 (__)-___-__-__",
                "type": "tel",
            }
        ),
        required=False,
    )

    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "text-field__input",
                "placeholder": "Email",
            }
        ),
        disabled=True,
    )

    birthday = forms.DateField(
        label="Birthday:",
        widget=forms.DateInput(
            attrs={
                "class": "text-field__input",
                "placeholder": "Birthday",
                "type": "date",
            },
        ),
        required=False,
    )

    sex = forms.ChoiceField(
        label="Gender:",
        choices=User.Sex.choices,
        widget=forms.Select(
            attrs={
                "class": "text-field__input",
                "placeholder": "Gender",
            }
        ),
    )

    city = forms.ChoiceField(
        label="City:",
        choices=User.Cities.choices,
        widget=forms.Select(
            attrs={
                "class": "text-field__input",
                "placeholder": "City",
            }
        ),
    )

    postcode = forms.IntegerField(
        label="Postcode:",
        min_value=10_000,
        max_value=99_999,
        widget=forms.NumberInput(
            attrs={
                "class": "text-field__input",
                "placeholder": "Postcode",
            }
        ),
        required=False,
    )

    background_cover = forms.FileField(
        label="Backgound cover",
        widget=forms.FileInput(
            attrs={
                "hidden": True,
                "accept": "image/*",
            }
        ),
        required=False,
    )

    photo = forms.ImageField(
        label="User avatar",
        widget=forms.FileInput(
            attrs={
                "hidden": True,
                "accept": "image/*",
            }
        ),
        required=False,
    )

    is_visible = forms.ChoiceField(
        label="Visibility:",
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), User.Visibility.choices)),
        widget=forms.Select(
            attrs={
                "class": "text-field__input",
                "placeholder": "Visibility",
                "style": "text-align: center; width: 80%; margin-bottom: 15px;",
            }
        ),
    )
