from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.core.validators import MaxValueValidator, MinValueValidator
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
    country = models.CharField(max_length=50, verbose_name="Author nationality")
    wiki_page = models.URLField(max_length=255, verbose_name="Link for wiki page")
    bio = models.TextField(blank=True, verbose_name="Author bio")
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
            .annotate(rating=F("total_rating") / F("total_review"))
            .order_by("-rating", "-total_review")
        )

    def new_books(self):
        return self.published().select_related("author").order_by("-time_create")


class BookManager(models.Manager):
    def get_queryset(self) -> BookQuerySet:
        return BookQuerySet(self.model)

    def published(self) -> BookQuerySet:
        return self.get_queryset().published()

    def top_rated(self) -> BookQuerySet:
        return self.get_queryset().top_rated()

    def new_books(self) -> BookQuerySet:
        return self.get_queryset().new_books()


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
    # book_page_cover ?
    publish_date = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1500),
            MaxValueValidator(datetime.today().year),
        ]
    )
    language = models.CharField(
        max_length=3,
        choices=Language.choices,
        default=Language.UNSELECTED,
        verbose_name="Book language",
    )
    pages = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10_000)],
        verbose_name="Amount of pages",
    )
    is_published = models.BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.DRAFT,  # type: ignore
        verbose_name="Book status",
    )
    description = models.TextField(blank=True, verbose_name="Book description")
    total_review = models.PositiveIntegerField(default=1)
    total_rating = models.PositiveIntegerField(default=5)
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


class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review_star = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ]
    )
    review_text = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Create time")

    def get_absolute_url(self) -> str:
        return reverse("Lib:home")
