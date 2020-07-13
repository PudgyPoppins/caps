from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from .models import User

class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('username', 'display_name', 'email')

class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model = User
		fields = ('username', 'display_name', 'email')

class UpdateUser(ModelForm):
	class Meta:
		model = User
		fields = ('username', 'display_name', 'email')
		help_texts = {'username': _(''), 'display_name': _(''), 'email': _('')}
