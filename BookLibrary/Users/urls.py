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
        views.UserPasswordChangeDoneView.as_view(),
        name="password-change-done",
    ),
    path(
        "password-reset/",
        views.UserPasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset/done",
        views.UserPasswordResetDoneView.as_view(),
        name="password-reset-done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset/complete/",
        views.UserPasswordResetCompleteView.as_view(),
        name="password-reset-complete",
    ),
]
