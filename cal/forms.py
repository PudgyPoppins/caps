import datetime

from django import forms
from django.forms import ModelForm#, CheckboxSelectMultiple
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Calendar, Event, Attendee

#The calendar form is ONLY used on the admin site, otherwise calendars are generated automatically
class CalendarAdminForm(ModelForm):
	class Meta:
		model = Calendar
		try:
			globalExists = Calendar.objects.get(isGlobal=True)
			exclude=('isGlobal',) #because this didn't throw up an error, global was found, so there's no need for an isGlobal anymore
		except: # if a calendar called global does NOT exist
			exclude=()#show the isGlobal field if the global calendar wasnt found
	def clean(self):
		user = self.cleaned_data['user']
		nonprofit = self.cleaned_data['nonprofit']
		network = self.cleaned_data['network']
		organization = self.cleaned_data['organization']
		try:
			global_cal = Calendar.objects.get(isGlobal=True) #global was found
			exclude=('isGlobal',)
		except:
			global_cal = None#global not found
		if not(user or nonprofit or network or organization) and global_cal is not None:#there has to be at least one of these forms
			raise ValidationError(_('You must fill out one of these fields (user, nonprofit, or network)'))
		if user and (nonprofit or network or organization) or nonprofit and (user or network or organization) or network and (user or nonprofit or organization) or organization and (user or nonprofit or network):
			raise ValidationError(_('Only one of these fields can be filled out (user, nonprofit, network)'))

class EventAdminForm(ModelForm):
	class Meta:
		model = Event
		exclude = ()
		widgets = {
			#'calendar': CheckboxSelectMultiple(), #this ended up being too long
			'description': forms.Textarea(), #we want that dummy thicc box for entering an entire description
		}
	def clean_end_time(self):
		end_time = self.cleaned_data.get('end_time')
		start_time = self.cleaned_data.get('start_time')
		end_date = self.cleaned_data.get('end_date')
		start_date = self.cleaned_data.get('start_date')

		if end_time and start_time and datetime.datetime.combine(end_date, end_time) <= datetime.datetime.combine(start_date, start_time):
			raise ValidationError(_('End time must be after start time'))
		if end_time and start_time and datetime.datetime.combine(end_date, end_time) - datetime.datetime.combine(start_date, start_time) < datetime.timedelta(minutes=10): #if the entire event lasts less than 10 minutes
			raise ValidationError(_('The event must be at least ten minutes long'))
		if not end_time and start_time:
			raise ValidationError(_('An end time is required if a start time is provided'))
		return end_time

	def clean_start_time(self):
		end_time = self.cleaned_data.get('end_time')
		start_time = self.cleaned_data.get('start_time')
		if not start_time and end_time:
			raise ValidationError(_('A start time is required if an end time is provided'))
		return start_time

	def clean_end_date(self):
		end_date = self.cleaned_data['end_date']
		start_date = self.cleaned_data['start_date']

		if end_date < start_date:
			raise ValidationError(_('End date must be after start date'))
		return end_date
	
	def clean_event_type(self):
		end_time = self.cleaned_data.get('end_time')
		start_time = self.cleaned_data.get('start_time')
		end_date = self.cleaned_data.get('end_date')
		start_date = self.cleaned_data.get('start_date')

		event_type = self.cleaned_data.get("event_type")
		if start_time and end_time and datetime.datetime.combine(end_date, end_time) - datetime.datetime.combine(start_date, start_time) > datetime.timedelta(days=1) and event_type == "VO": #if the entire event lasts more than 1 day, and it's a volunteering event
			raise ValidationError(_('A volunteering event cannot last for longer than one day'))
		return event_type

	def clean_sign_up_slots(self):
		sign_up_slots = self.cleaned_data['sign_up_slots']
		event_type = self.cleaned_data.get('event_type')
		if sign_up_slots and event_type != "VO":
			raise ValidationError(_('Only events with the type "Volunteering Opportunity" can have sign ups'))
		return sign_up_slots

	def save(self, commit=True):
		instance = super().save(commit=False)
		start_time = self.cleaned_data.get('start_time')
		end_time = self.cleaned_data.get('end_time')

		end_date = self.cleaned_data.get('end_date')
		start_date = self.cleaned_data.get('start_date')

		if start_time == datetime.time() and end_time == datetime.time() and start_date + datetime.timedelta(days=1) == end_date:#the event meets all the qualifications of an all_day event
			instance.all_day = True
		if self.cleaned_data.get('all_day'): #if this is an all day event, set the hour of the start_time to be 00:00, and the end_time to be one day later
			instance.start_time, instance.end_time = datetime.time(), datetime.time()
			instance.end_date = start_date + datetime.timedelta(days=1)
		if commit:
			instance.save()
		return instance

class EventForm(EventAdminForm):
	class Meta:
		model = Event
		exclude = ()
		widgets = {
			'description': forms.Textarea(), #we want that dummy thicc box for entering an entire description
			'start_date': forms.DateInput(attrs={'type': 'date'}),
			'end_date': forms.DateInput(attrs={'type': 'date'}),
			'start_time': forms.TimeInput(attrs={'type': 'time'}),
			'end_time': forms.TimeInput(attrs={'type': 'time'}),
		}
	def __init__(self, *args, **kwargs):
		super(EventForm, self).__init__(*args, **kwargs)
		self.fields.pop('calendar')
		self.fields.pop('token')
		self.fields.pop('created_by')
		self.fields.pop('excluded_dates')
		self.fields.pop('parent')
		self.fields.pop('verified')

		limited_choices = [(choice[0], choice[1]) for choice in self.fields['event_type'].choices if choice[0] != "AA"]
		self.fields['event_type'] = forms.ChoiceField(choices=limited_choices)# make event_type required, and limit the choices in there so Account Anniversary isn't selectable
		self.fields['event_type'].required = True

		self.fields['title'].required = True

class EventFormNetwork(EventForm):
	def __init__(self, *args, **kwargs):
		super(EventFormNetwork, self).__init__(*args, **kwargs)
		limited_choices = [(choice[0], choice[1]) for choice in self.fields['event_type'].choices if choice[0] != "AA" and choice[0] != "VO"]
		self.fields['event_type'] = forms.ChoiceField(choices=limited_choices)# limit choices further

class EventFormUpdate(EventForm):
	def __init__(self, *args, **kwargs):
		super(EventFormUpdate, self).__init__(*args, **kwargs)
		self.fields['event_type'].required = False
		self.fields['title'].required = False

class EventFormNetworkUpdate(EventFormNetwork):
	def __init__(self, *args, **kwargs):
		super(EventFormNetworkUpdate, self).__init__(*args, **kwargs)
		self.fields['event_type'].required = False
		self.fields['title'].required = False

class AttendeeForm(ModelForm):
	class Meta:
		model = Attendee
		fields = ['name', 'email']


CHANGE_CHOICES= [
	('t', 'This event'),
	('f', 'This and following events'),
	('a', 'This and all events'),
]
class RecurringEventForm(forms.Form):
	change_type= forms.CharField(label='', widget=forms.RadioSelect(choices=CHANGE_CHOICES))
	def clean_change_type(self):
		change_type = self.cleaned_data['change_type']
		if change_type != "t" and change_type != "f" and change_type != "a":
			raise ValidationError(_("Please stop trying to XSS the site :(. Just reload your browser page."))
		return change_type
