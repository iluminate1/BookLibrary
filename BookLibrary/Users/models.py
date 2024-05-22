from datetime import date
from django.core.validators import RegexValidator
from django.db import models
from typing import Any, Optional
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from BookLibrary.settings import MEDIA_URL


@deconstructible
class PostCodeLengthValidator:
    def __init__(self, message: Optional[str] = None) -> None:
        self.message = message if message else "Postcode must consist of 5 digits"

    def __call__(self, value: int) -> None:
        if len(str(value)) != 5:
            raise ValidationError(self.message, params={"value": value})


# Create your models here.
class User(AbstractUser):
    class Sex(models.TextChoices):
        UNSELECTED = "U", ("Unselected")
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    class Visibility(models.IntegerChoices):
        HIDDEN = 0, _("Hidden")
        VISIBLE = 1, _("Visible")

        # __empty__ = _("(Unknown)")

    class Cities(models.TextChoices):
        UNSELECTED = "UN", ("Unselected")
        MINSK = "MI", _("Minsk")
        GOMEL = "GO", _("Gomel")
        BREST = "BR", _("Brest")
        GRODNO = "GR", _("Grodno")
        MOGILEV = "MO", _("Mogilev")
        VITSYEBSK = "VI", _("Vitsyebsk")

    photo = models.ImageField(
        upload_to="users/photo/%Y/%m/%d/",
        default="Users/photo/default.png",
        verbose_name="User avatar",
    )
    birthday = models.DateField(
        null=True, blank=True, verbose_name="User birthday date"
    )
    postcode = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[PostCodeLengthValidator()],
        verbose_name="Postcode",
    )
    phone = models.CharField(
        blank=True,
        null=True,
        default=None,
        max_length=19,
        unique=True,
        validators=[
            RegexValidator(
                r"^(\+375) \((29|25|44|33)\) (\d{3})\-(\d{2})\-(\d{2})$",
                message=" Invalid phone number",
            )
        ],
        verbose_name="Phone number",
    )
    sex = models.CharField(max_length=1, choices=Sex.choices, default=Sex.UNSELECTED)
    background_cover = models.ImageField(
        upload_to="users/bg_cover/%Y/%m/%d/",
        default="Users/bg_cover/default.jpg",
        verbose_name="Profile backgound cover",
    )
    city = models.CharField(
        max_length=2,
        choices=Cities.choices,
        default=Cities.UNSELECTED,
        verbose_name="City",
    )

    is_visible = models.BooleanField(
        max_length=1,
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Visibility.choices)),
        default=Visibility.HIDDEN,  # type: ignore
        verbose_name="Profile visibility",
    )

    def __str__(self) -> str:
        return self.username

    def get_photo_url(self) -> str:
        return MEDIA_URL + str(self.photo)

    def get_bg_cover_url(self) -> str:
        return MEDIA_URL + str(self.background_cover)

    def get_age(self) -> Optional[str]:
        if self.birthday == None:
            return None
        age = str(date.today().year - self.birthday.year)  # type: ignore
        return f"( {age} )"

    def get_absolute_url(self):
        return reverse("User:user-profile", kwargs={"pk": self.pk})
