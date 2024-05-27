from datetime import date, datetime
from io import BytesIO
from pickle import NONE
from typing import Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import files
from django.db.models import F, Q, Count, Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, RedirectView, TemplateView

import requests
from slugify import slugify
from .openlibrary import API

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

        sort = self.request.GET.get("sort", None)
        match sort:
            case "popular":
                return Book.book.top_rated().filter(category__slug=self.kwargs["slug"])
            case "not_popular":
                return Book.book.unpopular().filter(category__slug=self.kwargs["slug"])
            case "newest":
                return Book.book.new_books().filter(category__slug=self.kwargs["slug"])
            case "oldest":
                return Book.book.old_books().filter(category__slug=self.kwargs["slug"])
            case _:
                return Book.book.top_rated().filter(category__slug=self.kwargs["slug"])

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
        sort = self.request.GET.get("sort", None)
        match sort:
            case "popular":
                return Book.book.top_rated()
            case "not_popular":
                return Book.book.unpopular()
            case "newest":
                return Book.book.new_books()
            case "oldest":
                return Book.book.old_books()
            case _:
                return Book.book.top_rated()


class SearchView(ListView):
    model = Book
    paginate_by = 8
    context_object_name = "books"
    http_method_names = ["get"]
    template_name = "Library/search.html"

    def get_queryset(self) -> QuerySet[Any]:
        publisher = self.request.GET.get("publisher", None)
        sort = self.request.GET.get("sort", None)
        if publisher:
            match sort:
                case "popular":
                    return Book.book.top_rated().filter(
                        Q(publisher_slug__icontains=publisher)
                    )
                case "not_popular":
                    return Book.book.unpopular().filter(
                        Q(publisher_slug__icontains=publisher)
                    )
                case "newest":
                    return Book.book.new_books().filter(
                        Q(publisher_slug__icontains=publisher)
                    )
                case "oldest":
                    return Book.book.old_books().filter(
                        Q(publisher_slug__icontains=publisher)
                    )
                case _:
                    return Book.book.top_rated().filter(
                        Q(publisher_slug__icontains=publisher)
                    )

        search = self.request.GET.get("q", None)
        if search:
            match sort:
                case "popular":
                    return Book.book.top_rated().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search)
                    )
                case "not_popular":
                    return Book.book.unpopular().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search)
                    )
                case "newest":
                    return Book.book.new_books().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search)
                    )
                case "oldest":
                    return Book.book.old_books().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search)
                    )
                case _:
                    return Book.book.top_rated().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search)
                    )

        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("q", "")
        publisher = self.request.GET.get("publisher", None)
        nkwargs = {
            "search": search,
            "publisher": publisher,
        }
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

        if self.request.user.is_authenticated:
            try:
                user_rate = UserRating.objects.values("rating").get(
                    user=self.request.user, book=book
                )
            except UserRating.DoesNotExist as e:
                user_rate = None
        else:
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


class ContributeView(LoginRequiredMixin, TemplateView):
    template_name = "Library/contribute.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        error_dict = {
            "show_error": True,
            "error_message": "Bibkey is not valid",
        }

        print(self.request.POST)

        key = self.request.POST.get("bibkey", None)
        method = self.request.POST.get("method", None)

        if not key:
            return self.render_to_response(error_dict)

        match method:
            case "ISBN":
                if not self.isISBN_valid(key):
                    context.update(error_dict)
                    return self.render_to_response(context=context)
            case "OLID":
                if not self.isOLID_valid(key):
                    context.update(error_dict)
                    return self.render_to_response(context=context)
            case _:
                context.update(
                    {
                        "show_error": True,
                        "error_message": "Method is not valid",
                    }
                )
                return self.render_to_response(context=context)

        try:
            api = API()
            book = api.get_book(id=key, bibkey=method).get_ready_dict()
        except Exception as e:
            print(e)
            return TemplateResponse(
                request,
                "Library/error.html",
                context={"message": "Cant't connect to openlibrary api"},
            )

        print(book)
        author, is_created = Author.objects.get_or_create(
            full_name=book["author"]["name"]
        )

        if is_created:
            author.bio = book["author"]["bio"]
            author.wiki_page = book["author"]["wikipedia"]
            author.slug = slugify(book["author"]["name"])
            try:
                url = book["author"]["photo"]
                resp = requests.get("https://" + url)
                if resp.status_code == requests.codes.ok:
                    print("Author created")
                    fp = BytesIO()
                    fp.write(resp.content)
                    file_name = url.split("/")[-1]
                    author.photo.save(file_name, files.File(fp))
            except:
                pass

            author.save()

        cat = Category.objects.get(pk=1)
        _book, is_created = Book.objects.get_or_create(
            name=book["title"], author=author, category=cat
        )

        if is_created:
            _book.name = book["title"]
            _book.slug = slugify(book["title"])
            _book.author = author
            _book.category = cat
            _book.description = book["desq"]
            _book.pages = book["num_pages"]
            _book.publisher = book["publishers"][0]
            _book.publisher_slug = slugify(book["publishers"][0])
            _book.preview = book["preview"]["embed"]
            _book.language = book["lang"]
            _book.is_published = Book.Status.PUBLISHED  # type: ignore
            _book.publish_date = book["publish_date"]

            try:
                url = book["cover"]["medium"]
                resp = requests.get(url)
                if resp.status_code == requests.codes.ok:
                    print("Book created")
                    fp = BytesIO()
                    fp.write(resp.content)
                    file_name = url.split("/")[-1]
                    _book.book_cover.save(file_name, files.File(fp))
            except:
                pass

            _book.save()

        return redirect(reverse_lazy("Lib:book", kwargs={"slug": _book.slug}))

    def isISBN_valid(self, isbn: str):
        if len(isbn) != 10 and len(isbn) != 13:
            return False

        if not isbn.isalnum():
            return False

        return True

    def isOLID_valid(self, olid: str) -> bool:
        if not olid.startswith("OL"):
            return False

        if not olid.endswith("M"):
            return False

        return True


class BorrowBookView(LoginRequiredMixin, RedirectView):
    http_method_names = ["post", "put", "patch"]

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("User:login"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        ref: str = request.META.get("HTTP_REFERER", "Lib:home")
        return HttpResponseRedirect(ref)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        book_id = self.request.POST.get("book_id", None)
        return_date = self.request.POST.get("return_date", None)

        if not return_date:
            return TemplateResponse(
                request,
                "Library/error.html",
                context={
                    "message": "Invalid return date",
                    "book": Book.objects.get(pk=book_id),
                },
            )

        converted_date = datetime.strptime(str(return_date), "%Y-%m-%d").date()

        is_valid, message = self.is_date_valid(converted_date)
        if is_valid:
            book = Book.objects.get(pk=book_id)
            user = get_user_model().objects.get(pk=request.user.pk)
            book.user = user
            book.is_taken = True
            book.return_date = converted_date
            book.save()
        else:
            return TemplateResponse(
                request,
                "Library/error.html",
                context={"message": message, "book": Book.objects.get(pk=book_id)},
            )

        return super().post(request, *args, **kwargs)

    def is_date_valid(self, return_date: date) -> tuple[bool, str]:
        today = datetime.now().date()
        if return_date < today:
            return False, "Return date must be more than today"

        delta = return_date - today
        if delta.days > 31:
            return False, "Maximum reservation period 31 days"

        return True, "Valid"


class ReturnBookView(LoginRequiredMixin, RedirectView):
    http_method_names = ["post", "put", "patch"]

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("User:login"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        ref: str = request.META.get("HTTP_REFERER", "Lib:home")
        return HttpResponseRedirect(ref)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        book_id = self.request.POST.get("book_id", None)
        user_id = self.request.user.pk
        user = get_user_model().objects.get(pk=user_id)

        book = Book.objects.get(pk=book_id)
        if book.user == user:
            book.user = None
            book.is_taken = False
            book.save()

        return super().post(request, *args, **kwargs)


class MyShelfView(LoginRequiredMixin, ListView):
    model = Book
    paginate_by = 8
    context_object_name = "books"
    http_method_names = ["get"]
    template_name = "Library/my_shelf.html"

    def get_queryset(self) -> QuerySet[Any]:
        sort = self.request.GET.get("sort", None)
        search = self.request.GET.get("q", None)
        user = get_user_model().objects.get(pk=self.request.user.pk)

        if search:
            match sort:
                case "popular":
                    return Book.book.top_rated().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search),
                        user=user,
                    )
                case "not_popular":
                    return Book.book.unpopular().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search),
                        user=user,
                    )
                case "newest":
                    return Book.book.new_books().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search),
                        user=user,
                    )
                case "oldest":
                    return Book.book.old_books().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search),
                        user=user,
                    )
                case _:
                    return Book.book.top_rated().filter(
                        Q(name__icontains=search)
                        | Q(category__name__icontains=search)
                        | Q(author__full_name__icontains=search),
                        user=user,
                    )

        match sort:
            case "popular":
                return Book.book.top_rated().filter(user=user)
            case "not_popular":
                return Book.book.unpopular().filter(user=user)
            case "newest":
                return Book.book.new_books().filter(user=user)
            case "oldest":
                return Book.book.old_books().filter(user=user)
            case _:
                return Book.book.top_rated().filter(user=user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("q", "")
        nkwargs = {
            "search": search,
        }
        context.update(nkwargs)
        return context
