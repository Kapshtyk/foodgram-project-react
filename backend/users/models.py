from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="электронная почта",
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name="юзернейм",
    )
    first_name = models.CharField(max_length=150, verbose_name="имя")
    last_name = models.CharField(max_length=150, verbose_name="фамилия")
    password = models.CharField(max_length=150, verbose_name="пароль")

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "username",
    ]
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ("email",)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="автор",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="подписчик",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
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
