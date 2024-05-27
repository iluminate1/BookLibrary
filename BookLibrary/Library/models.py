from datetime import datetime
from typing import Any, Optional
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Count, Sum
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    cover = models.ImageField(
        upload_to="Lib/category/cover/%Y/%m/%d/",
        default="Lib/category/cover/default.png",
        verbose_name="Category cover",
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Create time")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Update time")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("Lib:category", kwargs={"slug": self.slug})


class Author(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Full name")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    photo = models.ImageField(
        upload_to="Lib/author/photo/%Y/%m/%d/",
        default="Lib/author/photo/default.jpg",
        verbose_name="Author photo",
    )
    country = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Author nationality"
    )
    wiki_page = models.URLField(
        null=True, blank=True, max_length=255, verbose_name="Link for wiki page"
    )
    bio = models.TextField(null=True, blank=True, verbose_name="Author bio")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Create time")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Update time")

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self) -> str:
        return reverse("Lib:author", kwargs={"slug": self.slug})


class BookQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=Book.Status.PUBLISHED)

    def top_rated(self):
        return (
            self.select_related("author")
            .published()
            .annotate(total_view=Count("userrating__rating"))
            .annotate(top=Sum("userrating__rating") / Count("userrating__rating"))
            .order_by("-top", "-total_view")
        )

    def unpopular(self):
        return (
            self.select_related("author")
            .published()
            .annotate(total_view=Count("userrating__rating"))
            .annotate(top=Sum("userrating__rating") / Count("userrating__rating"))
            .order_by("top", "total_view")
        )

    def new_books(self):
        return self.published().select_related("author").order_by("-time_create")

    def old_books(self):
        return self.published().select_related("author").order_by("time_create")


class BookManager(models.Manager):
    def get_queryset(self) -> BookQuerySet:
        return BookQuerySet(self.model)

    def published(self) -> BookQuerySet:
        return self.get_queryset().published()

    def top_rated(self) -> BookQuerySet:
        return self.get_queryset().top_rated()

    def unpopular(self) -> BookQuerySet:
        return self.get_queryset().unpopular()

    def new_books(self) -> BookQuerySet:
        return self.get_queryset().new_books()

    def old_books(self) -> BookQuerySet:
        return self.get_queryset().old_books()


def save_pdf_path(instance, filename):
    return f"Lib/book/pdf/{instance.name}/{filename}"


class Book(models.Model):
    class Language(models.TextChoices):
        UNSELECTED = "UNS", _("Unknown")
        BY = "BY", _("Belarusian")
        RU = "RU", _("Russian")
        EN = "EN", _("Englisgh")

    class Status(models.IntegerChoices):
        DRAFT = 0, _("Draft")
        PUBLISHED = 1, _("Published")

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=125, db_index=True, unique=True)
    book_cover = models.ImageField(
        upload_to="Lib/book/cover/%Y/%m/%d/",
        default="Lib/book/cover/default.svg",
        verbose_name="Book cover",
    )
    pdf = models.FileField(
        null=True,
        blank=True,
        upload_to=save_pdf_path,
        verbose_name="Book pdf file",
    )
    user = models.ForeignKey(
        get_user_model(), models.SET_NULL, default=None, null=True, blank=True
    )
    is_taken = models.BooleanField(default=False)
    return_date = models.DateField(
        null=True,
        blank=True,
        auto_now=False,
        auto_now_add=False,
        auto_created=False,
        verbose_name="Return date",
    )
    publish_date = models.CharField(null=True, blank=True, max_length=10)
    publisher = models.CharField(max_length=200, verbose_name="Publisher")
    publisher_slug = models.SlugField(max_length=200, db_index=True)
    language = models.CharField(
        max_length=3,
        choices=Language.choices,
        default=Language.UNSELECTED,
        verbose_name="Book language",
    )
    pages = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10_000)],
        verbose_name="Amount of pages",
    )
    is_published = models.BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.DRAFT,  # type: ignore
        verbose_name="Book status",
    )
    preview = models.URLField(
        blank=True, null=True, verbose_name="URL for book preview"
    )

    description = models.TextField(blank=True, verbose_name="Book description")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Create time")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Update time")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    objects = models.Manager()
    book = BookManager()

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("Lib:book", kwargs={"slug": self.slug})


class UserRatingQuerySet(models.QuerySet):
    def total_rating(self, id: int):
        return (
            self.select_related("book", "user")
            .filter(book=id, rating__isnull=False)
            .aggregate(total_rating=Sum("rating"))
        )

    def total_review(self, id: int):
        return (
            self.select_related("book", "user")
            .filter(book=id, rating__isnull=False)
            .aggregate(total_review=Count("rating"))
        )

    def book_total(self, book_id: int):
        return (
            self.select_related("book", "user")
            .filter(book=book_id, rating__isnull=False)
            .aggregate(totla_rating=Sum("rating"), total_review=Count("rating"))
        )


class UserRatingManager(models.Manager):
    def get_queryset(self) -> UserRatingQuerySet:
        return UserRatingQuerySet(self.model)

    def total_rating(self, id) -> Optional[int]:
        return self.get_queryset().total_rating(id).get("total_rating", None)

    def total_review(self, id) -> Optional[int]:
        return self.get_queryset().total_review(id).get("total_review", None)

    def book_total(self, book_id: int) -> dict[str, int | None]:
        return self.get_queryset().book_total(book_id=book_id)


class UserRating(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        default=None,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    objects = models.Manager()
    book_rating = UserRatingManager()

    def __str__(self) -> str:
        return (
            f"Id={self.pk} BookId={self.book} UserId={self.user} Rating={self.rating}"
        )


class Review(models.Model):
    class Meta:
        ordering = ["-time_create"]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review_text = models.TextField(
        validators=[MinLengthValidator(10), MaxLengthValidator(400)],
        verbose_name="Review text",
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Create time")
