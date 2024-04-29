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
        default="users/default.jpg",
        verbose_name="User avatar",
    )
    birthday = models.DateField(blank=True, verbose_name="User birthday date")
    postcode = models.PositiveIntegerField(
        blank=True,
        validators=[PostCodeLengthValidator()],
        verbose_name="Postcode",
    )
    phone = models.CharField(
        blank=True,
        max_length=19,
        validators=[
            RegexValidator(
                r"^(\+375) \((29|25|44|33)\) (\d{3})\-(\d{2})\-(\d{2})$",
                message=" pInvalidhone number",
            )
        ],
        verbose_name="Phone number",
    )
    sex = models.CharField(max_length=1, choices=Sex.choices, default=Sex.UNSELECTED)
    background_cover = models.ImageField(
        upload_to="users/bg_cover/%Y/%m/%d/",
        default="users/default_bg_cover.jpg",
        verbose_name="User backgound cover",
    )
    city = models.CharField(
        max_length=2,
        choices=Cities.choices,
        default=Cities.UNSELECTED,
        verbose_name="City",
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
