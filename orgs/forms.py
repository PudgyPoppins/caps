import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Organization, Goal
#help_texts = {'lat': _('Please enter the latitude of the location, or leave it blank to auto-generate one via the address'), 'lon': _('Please enter the longitude of the location, or leave it blank to auto-generate one via the address')}
class OrganizationForm(ModelForm):
	class Meta:
		model = Organization
		#fields = ['title', 'src_link', 'src_file', 'leader', 'moderator', 'public']
		exclude = ('slug', 'leader', 'member', 'moderator')
		labels = {'src_link': _('Image Url'), 'src_file': _('Image File')}
		widgets = {
			'description': forms.Textarea(),
		}

	def clean_src_file(self):
		image = self.cleaned_data.get('src_file', False)
		if image:
			if image._size > 2.5*1024*1024:
				raise ValidationError("Image file too large ( > 2.5MB )")
		return image

	def clean(self):
		file = self.cleaned_data.get('src_file', False)
		url = self.cleaned_data.get('src_link', False)
		if url and file:
			raise ValidationError(_("You cannot upload both an image url and an image file. Please upload one or the other."))

class TransferLeadership(ModelForm):
	class Meta:
		model = Organization
		fields = ['leader']
		labels = {'leader': _('Transfer leadership of this organization to another user'),}

class GoalForm(ModelForm):
	class Meta:
		model = Goal
		exclude = ('',)
		widgets = {
			'description': forms.Textarea(),
		}
	def clean(self):
		if self.cleaned_data['start'] is not None and self.cleaned_data['end'] is not None:
			if self.cleaned_data['end'] <= self.cleaned_data['start']:
				raise ValidationError(_("The ending date must be after the starting time"))
			if self.cleaned_data['end'] - self.cleaned_data['start'] < datetime.timedelta(days=1):
				raise ValidationError(_("The ending date must at least one day ahead of the starting date"))