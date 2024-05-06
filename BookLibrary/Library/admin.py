from django.contrib import admin
from django.utils.safestring import SafeText, mark_safe

from BookLibrary.settings import MEDIA_URL

from .models import Author, Book, Category


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "img_preview")
    fields = ("name", "slug", "cover", "img_preview")
    readonly_fields = ("img_preview",)
    prepopulated_fields = {"slug": ("name",)}
    save_on_top = True

    @admin.display(description="Category cover preview")
    def img_preview(self, cat: Category) -> SafeText:
        return mark_safe(
            f"<a href='{MEDIA_URL + str(cat.cover)}'><img src='{MEDIA_URL + str(cat.cover)}' title='{MEDIA_URL + str(cat.cover)}' width=50></a>"
        )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "slug", "country", "bio")
    fields = (
        "full_name",
        "slug",
        "bio",
        "country",
        "wiki_page",
        "photo",
        "img_preview",
        "time_create",
        "time_update",
    )
    readonly_fields = ("time_create", "time_update", "img_preview")
    prepopulated_fields = {"slug": ("full_name",)}
    save_on_top = True

    @admin.display(description="Author photo preview")
    def img_preview(self, author: Author) -> SafeText:
        return mark_safe(
            f"<a href='{MEDIA_URL + str(author.photo)}'><img src='{MEDIA_URL + str(author.photo)}' title='{MEDIA_URL + str(author.photo)}' width=50></a>"
        )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "author",
        "category",
        "publish_date",
        "language",
        "pages",
        "is_published",
    )
    prepopulated_fields = {"slug": ("name",)}
    save_on_top = True
