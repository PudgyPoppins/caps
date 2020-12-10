from django import forms
from django.utils import timezone
from datetime import timedelta
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.dateparse import parse_duration

from .models import Log

class LogForm(ModelForm):
	class Meta:
		model = Log
		fields = ['start_date', 'duration', 'description', 'nonprofit']#, 'nonprofit_text']
		widgets = {
			'nonprofit': forms.HiddenInput(), 
			'description': forms.Textarea(),
			'start_date': forms.DateInput(attrs={'type': 'date'}),
			#'nonprofit_text':forms.HiddenInput()
		}
	
	def clean_start_date(self):
		start = self.cleaned_data['start_date']
		#you can't log volunteer dates in the future, and you can't log volunteer dates more than 7 days in the past
		if start > timezone.now().date():
			raise ValidationError(_('Invalid start date - cannot be in the future'))
		elif start < timezone.now().date() - timedelta(days=7):
			raise ValidationError(_('Invalid start date - must log hours within 7 days of completing volunteering'))
		# Remember to always return the cleaned data.
		return start

	def clean_duration(self):
		duration = self.cleaned_data['duration']
		duration_parsed = parse_duration(str(duration))
		if not duration_parsed:
			raise ValidationError(_('Invalid duration - this format could not be understood'))
		elif (duration_parsed * 60) < timedelta(minutes=15): #*60 so it reads as minutes, not seconds
			raise ValidationError(_('Invalid duration - must be at least 15 minutes'))
		return duration

	'''def clean(self):
		np = self.cleaned_data['nonprofit']
		np_text = self.cleaned_data['nonprofit_text']
		if not(np ^ np_text):
			raise ValidationError(_('One of these fields, but not both, is required: nonprofit and nonprofit_text'))'''
	
	#For some reason is wasn't being required :(
	def clean(self):
		try:
			np = self.cleaned_data['nonprofit']
		except:
			raise ValidationError(_('You must select a nonprofit'))

	def __init__(self, *args, **kwargs):
		super(LogForm, self).__init__(*args, **kwargs)
		self.fields['nonprofit'].required = True