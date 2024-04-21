from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginUserForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password"]

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

    email = forms.CharField(
        label="email",
        widget=forms.TextInput(
            attrs={
                "class": "form__input",
                "type": "email",
                "placeholder": "Email",
            }
        ),
    )

    password1 = forms.CharField(
        label="password1",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="password2",
        widget=forms.PasswordInput(
            attrs={
                "class": "form__input",
                "type": "password",
                "placeholder": "Repeat Password",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registred!")
        return email
