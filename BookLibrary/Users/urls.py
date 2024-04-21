from django.contrib.auth.views import LogoutView, PasswordChangeDoneView
from django.urls import path, reverse_lazy

from . import views

app_name = "User"

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.LogoutUserView.as_view(), name="logout"),
    path("registr/", views.RegisterUserView.as_view(), name="registr"),
    path(
        "password-change/",
        views.UserPasswordChangeView.as_view(),
        name="password-change",
    ),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="Users/change_password_done.html", title="Password changed"
        ),
        name="password_change_done",
    ),
]
