from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

class User(AbstractUser):
    pass
    username = models.CharField(max_length=25, help_text="What username would you like to pick?", unique=True, default="")
    email = models.EmailField(max_length=254, help_text="What email are you gonna use?", unique=True, default="")

    def __str__(self):
        return self.username