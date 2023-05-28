from django.db import models
from  django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]
    USERNAME_FIELD = "username"