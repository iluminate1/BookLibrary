from django.urls import path

from .views import (
    AddCommentView,
    AuthorView,
    BookView,
    CategoryView,
    IndexView,
    LibraryView,
    RateBookView,
    SearchView,
)


app_name = "Lib"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("book/<slug:slug>/", BookView.as_view(), name="book"),
    path("book/<slug:slug>/add-comment/", AddCommentView.as_view(), name="book_add"),
    path("book/<slug:slug>/rate/", RateBookView.as_view(), name="book_rate"),
    path("author/<slug:slug>", AuthorView.as_view(), name="author"),
    path("category/all/", LibraryView.as_view(), name="library"),
    path("category/<slug:slug>", CategoryView.as_view(), name="category"),
    path("search/", SearchView.as_view(), name="search"),
]
