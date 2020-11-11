from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orgs.models import TextPost

class CreateAnnouncement(ModelForm):
	class Meta:
		model = TextPost
		fields = ('title', 'message', 'allows_children')
		widgets = {'message': forms.Textarea()}

class ReplyAnnouncement(CreateAnnouncement):
	def __init__(self, *args, **kwargs):
		super(ReplyAnnouncement, self).__init__(*args, **kwargs)
		self.fields.pop('allows_children')
		self.fields.pop('title')