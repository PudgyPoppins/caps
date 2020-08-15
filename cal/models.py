from django.db import models

from django.urls import reverse

import datetime, random, string
from django.utils import timezone
import datetime

from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.models import User
from network.models import Network, Nonprofit
from orgs.models import Organization

from django.core.validators import RegexValidator

rruleValidator = RegexValidator(r'[^><.\"\'&a-mo-z!@#$%^&*()+_\s]+', 'This string must be in the rrule format.') #currently, doesn't enforce rrule formate that well

# Create your models here.

def create_token():
	chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
	token = ''.join(random.choice(chars) for _ in range(5))
	token_list = Calendar.objects.filter(token=token)
	while token_list:
		token = ''.join(random.choice(chars) for _ in range(5))
		token_list = Calendar.objects.filter(token=token)
	return token
class Calendar(models.Model):
	token = models.CharField(max_length=5, null=True, blank=True) #token is the uniqueness part
	
	user = models.OneToOneField(User, on_delete=models.CASCADE, null = True, blank = True)
	nonprofit = models.OneToOneField(Nonprofit, on_delete=models.CASCADE, null = True, blank = True)
	network = models.OneToOneField(Network, on_delete=models.CASCADE, null = True, blank = True)
	organization = models.OneToOneField(Organization, on_delete=models.CASCADE, null = True, blank = True)

	network_calendar = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="networkcal") #network calendars consist of multiple nonprofit calendars, + their own events
	
	custom_calendar = models.ForeignKey('self', on_delete=models.SET_NULL, null = True, blank = True, related_name="calendars") #user and organization calendars can consist of multiple network and nonprofit calendars, + their own events
	excluded_calendars = models.ForeignKey('self', on_delete=models.SET_NULL, null = True, blank = True, related_name="excludedcal") #users and orgs can choose to exclude certain nonprofit calendars from their user calendars

	isGlobal = models.BooleanField(default=False)

	def __str__(self):
		if(self.user):
			return format(self.user.username)
		elif(self.nonprofit):
			return format(self.nonprofit.slug)
		elif(self.network):
			return format(self.network.slug)
		elif(self.organization):
			return format(self.organization.slug)
		else:
			return ("Global")
	def save(self, *args, **kwargs):
		if not self.token:
			self.token = create_token() #set the token on save
		return super(Calendar, self).save(*args, **kwargs)

class ExcludedDates(models.Model):
	date = models.DateField('excluded date', default=datetime.date.today)
	def __str__(self):
		return self.date.strftime('%Y%m%d')

def create_token_event():
	chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
	token = ''.join(random.choice(chars) for _ in range(5))
	token_list = Event.objects.filter(token=token)
	while token_list:
		token = ''.join(random.choice(chars) for _ in range(5))
		token_list = Event.objects.filter(token=token)
	return token

class Event(models.Model):
	title = models.CharField(help_text="What is the name of the event?", max_length=75, blank = True, null = True) #null is true because the children can inherit from the parent
	description = models.CharField(help_text='Describe the event briefly. What type of work will be done?', max_length=1000, blank = True, null = True)
	token = models.CharField(max_length=5, null=True, blank=True) #token is the uniqueness part

	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True, related_name="created_by")

	start_date = models.DateField('starting date', default=datetime.date.today)
	end_date = models.DateField('ending date', default=datetime.date.today)
	start_time = models.TimeField('starting time', null=True, blank=True)
	end_time = models.TimeField('ending time', null=True, blank=True)

	all_day = models.BooleanField('all day?', help_text="will this event last the entire day", default=False, null=True)
	rrule = models.CharField(help_text="Will this event ever repeat?", null = True, blank = True, max_length=700, validators=[rruleValidator])
	
	excluded_dates = models.ManyToManyField(ExcludedDates, blank = True, related_name="excluded")

	class event_type_choices(models.TextChoices):
		VO = 'VO', _('Volunteering Opportunity') #Network events cannot access this
		AA = 'AA', _('Account Anniversary') #This will never appear as an option to users
		CE = 'CE', _('Community Event') #Network events are automatically set to community events
		NV = 'NV', _('Non-Volunteering Event')

		#Network events: CE, NV
		#Nonprofit events: CE, NV, VO
		#User events: CE, NV, VO

	event_type = models.CharField(
		help_text="What type of event will this be?",
		max_length=2,
		choices=event_type_choices.choices,
		#default=event_type_choices.NV,
		blank = True, null = True, #this makes it so that the children don't have to be filled, inherit from the parent
	)

	verified = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True, help_text="has a nonprofit representative verified this network?")

	calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, null = True, blank = True, related_name="event")

	sign_up_slots = models.IntegerField(help_text="How many sign up slots are being offered?", null = True, blank = True, validators=[MinValueValidator(1), MaxValueValidator(100)])

	parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="instance") #relates to itself

	@property
	def s_title(self): #the s stands for search, it automatically does a check so I don't have to
		if self.title:
			return self.title
		elif self.parent:
			return self.parent.s_title
		else:
			return "uh oh, this shouldn't be read"
	@property
	def s_event_type(self):
		if self.event_type:
			return self.event_type
		elif self.parent:
			return self.parent.s_event_type
		else:
			return "uh oh, this shouldn't be read"
	@property
	def s_start_time(self):
		if self.start_time:
			return self.start_time
		elif self.parent:
			return self.parent.s_start_time
		else:
			return datetime.time()
	@property
	def s_sign_up_slots(self):
		if self.sign_up_slots:
			return self.sign_up_slots
		elif self.parent:
			return self.parent.s_sign_up_slots
		else:
			return None
	@property
	def s_end_time(self):
		if self.end_time:
			return self.end_time
		elif self.parent:
			return self.parent.s_end_time
		else:
			return datetime.time()
	@property
	def s_created_by(self):
		if self.created_by:
			return self.created_by
		elif self.parent:
			return self.parent.s_created_by
		else:
			return None
	@property
	def s_description(self):
		if self.description:
			return self.description
		elif self.parent:
			return self.parent.s_description
		else:
			return None
	@property
	def s_calendar(self):
		if self.calendar:
			return self.calendar
		elif self.parent:
			return self.parent.s_calendar
		else:
			return None
	@property
	def s_all_day(self):
		if self.all_day is not None:
			return self.all_day
		elif self.parent:
			return self.parent.s_all_day
		else:
			return "uh oh, this shouldn't be read"
	@property
	def s_verified(self):
		if self.verified is not None:
			return self.verified
		elif self.parent:
			return self.parent.s_verified
		else:
			return None

	'''def s_field(self, field):
		# was a really great way to search through fields without all of these properties, but couldn't be called in templates, and I didn't want to include custom filters on every page :(
		if getattr(self, field) is not None:
			return getattr(self, field)
		elif self.parent:
			return self.parent.s_field(field)
		else:
			return None'''

	@property
	def cal_type(self):
		if self.s_calendar:
			if self.s_calendar.nonprofit:
				return "nonprofit"
			elif self.s_calendar.network:
				return "network"
			elif self.s_calendar.organization:
				return "organization"
			elif self.s_calendar.user:
				return "user"
		else:
			return None

	@property
	def cal_url(self):
		if self.s_calendar:
			if self.s_calendar.nonprofit:
				return reverse('network:detailnon', kwargs={'network' : self.s_calendar.nonprofit.network.slug, 'slug' : self.s_calendar.nonprofit.slug}) + "#calendar"
			elif self.s_calendar.network:
				return reverse('network:detail', kwargs={'slug' : self.s_calendar.network.slug}) + "#calendar"
			elif self.s_calendar.organization:
				return reverse('organization:detail', kwargs={'slug' : self.s_calendar.organization.slug}) + "#calendar"
			elif self.s_calendar.user:
				return reverse('accounts:profile') + "#calendar"
			else:
				return reverse('home:main')
		else:
			return None

	@property
	def start_datetime(self):
		return datetime.datetime.combine(self.start_date, self.s_start_time).replace(tzinfo=timezone.get_current_timezone())
	@property
	def end_datetime(self):
		return datetime.datetime.combine(self.end_date, self.s_end_time).replace(tzinfo=timezone.get_current_timezone())


	class Meta: 
		ordering = ['parent__id', '-start_date']

	def __str__(self):
		return format(self.s_title)

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = create_token_event() #set the token on save
		return super(Event, self).save(*args, **kwargs)

class Attendee(models.Model):
	name = models.CharField(max_length=50)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
	email = models.EmailField(max_length=50, blank = True, null=True)
	event = models.ForeignKey(Event, on_delete=models.CASCADE, null = True, related_name="attendee")
	def __str__(self):
		if self.user:
			return format(self.user)
		elif self.name:
			return format(self.name)