from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import User

# Register your models here.


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
    )

    list_display_links = ('id', 'username')

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
            {"fields": ("birthday", "photo", "user_photo")},
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
            {"fields": ("birthday",)},
        ),
    )

    # Settings
    save_on_top = True
    readonly_fields = ("user_photo",)

    @admin.display(description="Avatar Preview", ordering="content")
    def user_photo(self, user: User):
        if user.photo:
            return mark_safe(
                f"<a href='{user.get_photo_url()}'><img src='{user.get_photo_url()}' title='{user.get_photo_url()}' width=50></a>"
            )
        return "Default"
