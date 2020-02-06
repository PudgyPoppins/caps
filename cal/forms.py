import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Calendar, Event

#The calendar form is ONLY used on the admin site, otherwise calendars are generated automatically
class CalendarAdminForm(ModelForm):
	class Meta:
		model = Calendar
		try:
			globalExists = Calendar.objects.get(title='Global')
			exclude=('title',) #because this didn't throw up an error, global was found, so there's no need for a title anymore
		except: # if a calendar called global does NOT exist
			exclude=()#show the title field if the global calendar wasnt found
	def clean(self):
		user = self.cleaned_data['user']
		nonprofit = self.cleaned_data['nonprofit']
		network = self.cleaned_data['network']
		try:
			title = Calendar.objects.get(title='Global') #global was found
			exclude=('title',)
		except:
			title = None#global not found
		if not(user or nonprofit or network) and title is not None:#there has to be at least one of these forms
			raise ValidationError(_('You must fill out at least one of these fields (user, nonprofit, or network)'))
		if user and (nonprofit or network):
			raise ValidationError(_('If a user is specified, neither a network nor nonprofit can be chosen'))

	def save(self, commit=True): #sets the title if it isn't set yet
		instance = super().save(commit=False)
		if self.cleaned_data.get('title') is None: #title not set yet
			if self.cleaned_data.get('user') is not None:
				title = self.cleaned_data.get('user').username + "-cal"
			elif self.cleaned_data.get('nonprofit') is not None:
				title = self.cleaned_data.get('nonprofit').title + "-cal"
			elif self.cleaned_data.get('network') is not None:
				title = self.cleaned_data.get('network').title + "-cal"
			instance.title = title
		if commit:
			instance.save()
		return instance


class EventForm(ModelForm):
	class Meta:
		model = Event
		exclude = ()
		#labels = {'start_time': _('Start Time'), }
		widgets = {
			'calendar': forms.HiddenInput(), #a javascript script will populate this field
			'description': forms.Textarea(), #we want that dummy thicc box for entering an entire description
		}
	def clean_end_time(self):
		end_time = self.cleaned_data['end_time']
		start_time = self.cleaned_data['end_time']
		if end_time <= start_time:
			raise ValidationError(_('End time must after start time'))
		return data
	
	def clean(self):
		start_time = self.cleaned_data['end_time']
		end_time = self.cleaned_data['end_time']
		if start_time - end_time < datetime.timedelta(minutes=10): #if the entire event lasts less 10 minutes
			raise ValidationError(_('The event must be at least ten minutes long'))