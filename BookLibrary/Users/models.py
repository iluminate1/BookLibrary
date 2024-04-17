from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    photo = models.ImageField(
        upload_to="users/%Y/%m/%d/",
        default=f"users/default.jpg",
        blank=True,
        null=True,
        verbose_name="User avatar",
    )
    birthday = models.DateTimeField(
        blank=True, null=True, verbose_name="User birthday date"
    )

    def __str__(self) -> str:
        return self.username

    def get_photo_url(self) -> str: 
        return f"/media/{self.photo}"
