from django.views.generic import TemplateView


# Create your views here.
class ProfileView(TemplateView):
    template_name = "Users/profile.html"
    http_method_names = ['get']

    