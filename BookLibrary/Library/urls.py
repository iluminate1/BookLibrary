from django.urls import path

from .views import (
    AddCommentView,
    AuthorView,
    BookView,
    BorrowBookView,
    CategoryView,
    ContributeView,
    IndexView,
    LibraryView,
    MyShelfView,
    RateBookView,
    ReturnBookView,
    SearchView,
)


app_name = "Lib"

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("book/<slug:slug>/", BookView.as_view(), name="book"),
    path("book/<slug:slug>/add-comment/", AddCommentView.as_view(), name="book_add"),
    path("book/<slug:slug>/rate/", RateBookView.as_view(), name="book_rate"),
    path("book/<slug:slug>/borrow/", BorrowBookView.as_view(), name="book_borrow"),
    path("book/<slug:slug>/return/", ReturnBookView.as_view(), name="book_return"),
    path("my-shelf/", MyShelfView.as_view(), name="my_shelf"),
    path("contribute/", ContributeView.as_view(), name="contribute"),
    path("author/<slug:slug>", AuthorView.as_view(), name="author"),
    path("library/", LibraryView.as_view(), name="library"),
    path("category/<slug:slug>", CategoryView.as_view(), name="category"),
    path("search/", SearchView.as_view(), name="search"),
]
