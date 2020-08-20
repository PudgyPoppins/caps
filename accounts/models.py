from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
	pass
	username = models.CharField(max_length=25, help_text="What username would you like to pick?", unique=True, default="")
	email = models.EmailField(max_length=254, help_text="What email are you gonna use?", unique=True, default="")
	display_name = models.CharField(max_length=50, help_text="This is the name that others will see you as (if specified)", blank=True, null=True)

	def __str__(self):
		if self.display_name:
			return self.display_name
		return self.username