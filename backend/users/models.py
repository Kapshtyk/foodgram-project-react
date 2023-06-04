from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="email",
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name="username",
    )
    first_name = models.CharField(max_length=150, verbose_name="first_name")
    last_name = models.CharField(max_length=150, verbose_name="last_name")
    password = models.CharField(max_length=150, verbose_name="password")

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "username",
    ]
    USERNAME_FIELD = "email"

    class Meta:
        ordering = ("email",)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"],
                name="unique_following",
            )
        ]

    def clean(self):
        if self.author == self.user:
            raise ValidationError("Cannot subscribe to yourself.")

    def __str__(self):
        return f"{self.author} follows {self.user}"
