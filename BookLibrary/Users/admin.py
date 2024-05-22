from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe

from .models import User

# Register your models here.


class SexFilter(admin.SimpleListFilter):
    title = "Sex"
    parameter_name = "sex"

    def lookups(self, request, model_admin):
        return [
            ("U", "Unselected"),
            ("M", "Male"),
            ("F", "Female"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case User.Sex.UNSELECTED as search:
                return queryset.filter(sex=search)
            case User.Sex.MALE as search:
                return queryset.filter(sex=search)
            case User.Sex.FEMALE as search:
                return queryset.filter(sex=search)


class CityFilter(admin.SimpleListFilter):
    title = "City"
    parameter_name = "city"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ("UN", "Unselected"),
            ("MI", "Minsk"),
            ("GO", "Gomel"),
            ("BR", "Brest"),
            ("GR", "Grodno"),
            ("MO", "Mogilev"),
            ("VI", "Vitsyebsk"),
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        match self.value():
            case User.Cities.UNSELECTED as search:
                return queryset.filter(city=search)
            case User.Cities.MINSK as search:
                return queryset.filter(city=search)
            case User.Cities.GOMEL as search:
                return queryset.filter(city=search)
            case User.Cities.BREST as search:
                return queryset.filter(city=search)
            case User.Cities.GRODNO as search:
                return queryset.filter(city=search)
            case User.Cities.MOGILEV as search:
                return queryset.filter(city=search)
            case User.Cities.VITSYEBSK as search:
                return queryset.filter(city=search)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # ListView
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "user_photo",
        "view_profile",
    )

    list_display_links = ("id", "username")

    # DetailView
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Additional info",
            {
                "fields": (
                    "birthday",
                    "photo",
                    "user_photo",
                    "phone",
                    "postcode",
                    "sex",
                    "city",
                    "background_cover",
                    "bg_cover",
                    "is_visible",
                )
            },
        ),
    )

    # AddView
    add_fieldsets = (
        (None, {"fields": ("username", "password1", "password2")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Additional info",
            {
                "fields": (
                    "birthday",
                    "sex",
                    "city",
                )
            },
        ),
    )

    # Settings
    save_on_top = True
    readonly_fields = ("user_photo", "bg_cover")
    search_fields = [
        "id",
        "username",
        "email",
    ]
    list_filter = [SexFilter, CityFilter]

    @admin.display(description="Avatar Preview", ordering="content")
    def user_photo(self, user: User):
        if user.photo:
            return mark_safe(
                f"<a href='{user.get_photo_url()}'><img src='{user.get_photo_url()}' title='{user.get_photo_url()}' width=50></a>"
            )
        return "Default"

    @admin.display(description="Bg. cover preview", ordering="content")
    def bg_cover(self, user: User):
        if user.background_cover:
            return mark_safe(
                f"<a href='{user.get_bg_cover_url()}'><img src='{user.get_bg_cover_url()}' title='{user.get_bg_cover_url()}' width=200px></a>"
            )
        return "Default"

    @admin.display(description="View user profile")
    def view_profile(self, user: User):
        return mark_safe(f'<a href="{user.get_absolute_url()}">VIEW</a>')
