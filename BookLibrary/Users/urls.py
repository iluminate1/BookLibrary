from django.urls import path, reverse_lazy

from . import views

app_name = 'User'

urlpatterns = [
    path('profile/', views.ProfileView.as_view())
]