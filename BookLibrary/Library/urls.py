from django.urls import path

from .views import AuthorView, CategoryView, IndexView, LibraryView


app_name = "Lib"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("book/<slug:slug>", IndexView.as_view(), name="book"),
    path("author/<slug:slug>", AuthorView.as_view(), name="author"),
    path("category/<slug:slug>", CategoryView.as_view(), name="category"),
    path("category/all/", LibraryView.as_view(), name="library"),
]
