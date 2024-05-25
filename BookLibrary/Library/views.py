import datetime
import re
from typing import Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect, request
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, RedirectView, TemplateView

from .models import Author, Book, Category, Review, UserRating


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
    template_name = "Library/search.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Book.book.top_rated()


class SearchView(ListView):
    model = Book
    paginate_by = 8
    context_object_name = "books"
    http_method_names = ["get"]
    template_name = "Library/search.html"

    def get_queryset(self) -> QuerySet[Any]:
        publisher = self.request.GET.get("publisher", None)
        if publisher:
            return Book.book.top_rated().filter(Q(publisher_slug__icontains=publisher))

        search = self.request.GET.get("q", None)
        if search:
            return Book.book.top_rated().filter(
                Q(name__icontains=search)
                | Q(category__name__icontains=search)
                | Q(author__full_name__icontains=search)
            )
        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("q", "")
        nkwargs = {"search": search}
        context.update(nkwargs)
        return context


class BookView(TemplateView):
    template_name = "Library/book.html"
    http_method_names = ["get", "post"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        error = self.request.GET.get("error", None)

        if not error:
            return super().get(request, *args, **kwargs)

        errors = error.split("?")

        if len(errors) > 1:
            return redirect(self.request.path + "?" + errors[-1])

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        error = self.request.GET.get("error", None)
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book.book, slug=self.kwargs["slug"])
        comments = Review.objects.select_related("user").filter(book=book)

        try:
            user_rate = UserRating.objects.values("rating").get(
                user=self.request.user, book=book
            )
        except UserRating.DoesNotExist as e:
            user_rate = None

        arr = range(5, 0, -1)
        nkwargs = {
            "book": book,
            "comments": comments,
            "error": error,
            "user_rate": user_rate,
            "stars": arr,
        }
        context.update(nkwargs)
        return context


class AddCommentView(LoginRequiredMixin, RedirectView):
    http_method_names = ["post", "put", "patch"]
    error_message = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("User:login"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.error_message:
            return HttpResponseRedirect(
                request.META.get("HTTP_REFERER", "Lib:home")
                + f"?error={self.error_message}"
            )

        ref: str = request.META.get("HTTP_REFERER", "Lib:home")
        _ref = ref.split("?")[0]

        return HttpResponseRedirect(_ref)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user_id = int(self.request.user.pk)
        book_id = int(self.request.POST.get("book_id")[0])  # type:ignore
        comment_text = self.request.POST.get("text", None)

        if not comment_text:
            self.error_message = "Comment must not be empty"
            return super().post(request, *args, **kwargs)

        if len(comment_text) < 10 or len(comment_text) > 400:
            self.error_message = "Comment length must be in range [10, 400] symbols"
            return super().post(request, *args, **kwargs)

        try:
            user = get_user_model().objects.get(pk=user_id)
            book = Book.objects.get(pk=book_id)
            Review.objects.create(user=user, book=book, review_text=comment_text)
        except Exception as e:
            print(e)
            self.error_message = "Can't add your comment to database"

        return super().post(request, *args, **kwargs)


class RateBookView(LoginRequiredMixin, RedirectView):
    http_method_names = ["post", "put", "patch"]

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("User:login"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        ref: str = request.META.get("HTTP_REFERER", "Lib:home")
        return HttpResponseRedirect(ref)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        rate_value = request.POST.get("rate", None)
        book_id = request.POST.get("book_id")
        user_id = int(request.user.pk)
        should_delete = request.POST.get("delete", False)

        if should_delete:
            user = get_user_model().objects.get(pk=user_id)
            book = Book.objects.get(pk=book_id)
            UserRating.objects.get(user=user, book=book).delete()
            return super().post(request, *args, **kwargs)

        if not rate_value:
            return super().post(request, *args, **kwargs)

        try:
            user = get_user_model().objects.get(pk=user_id)
            book = Book.objects.get(pk=book_id)
        except Exception as e:
            print(e)
            return super().post(request, *args, **kwargs)

        user_rate, created = UserRating.objects.get_or_create(user=user, book=book)
        user_rate.rating = int(rate_value)
        user_rate.save()

        return super().post(request, *args, **kwargs)
