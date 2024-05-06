from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView

from .models import Author, Book, Category


class IndexView(TemplateView):
    template_name = "Library/index.html"
    http_method_names = ["get"]
    extra_context = {"title": "BookLibrary"}

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        top_rated_books = Book.book.top_rated()[:4]
        new_books = Book.book.new_books()[:15]
        cats = Category.objects.all().order_by("name")
        nkwargs = {
            "top_books": top_rated_books,
            "new_books": new_books,
            "cats": cats,
        }
        context.update(nkwargs)
        return context


class AuthorView(TemplateView):
    template_name = "Library/author.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(Author.objects, slug=self.kwargs["slug"])
        related_books = Book.book.top_rated().filter(author=author)
        nkwargs = {
            "title": author.full_name,
            "author": author,
            "related_books": related_books,
        }
        context.update(nkwargs)
        return context


class CategoryView(ListView):
    model = Book
    paginate_by = 8
    context_object_name = "books"
    http_method_names = ["get"]
    template_name = "Library/category.html"

    def get_queryset(self) -> QuerySet[Any]:
        return (
            Book.book.select_related("author")
            .published()
            .filter(category__slug=self.kwargs["slug"])
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        category = Category.objects.values("name").get(slug=self.kwargs["slug"])
        nkwargs = {"category": category}
        context.update(nkwargs)
        return context


class LibraryView(ListView):
    model = Book
    paginate_by = 8
    context_object_name = "books"
    http_method_names = ["get"]
    template_name = "Library/category.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Book.book.top_rated()
