from django.db import models

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
	date = models.DateField('excluded date', default=timezone.now)

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

	start_time = models.DateTimeField('starting time', default=timezone.now)
	end_time = models.DateTimeField('ending time', default=timezone.now)
	all_day = models.BooleanField('all day?', help_text="will this event last the entire day", default=False)
	rrule = models.CharField(help_text="Will this event ever repeat?", null = True, blank = True, max_length=700, validators=[rruleValidator])
	
	excluded_dates = models.ManyToManyField(ExcludedDates, blank = True, related_name="excluded")

	class event_type_choices(models.TextChoices):
		VO = 'VO', _('Volunteering Opportunity') #Network events cannot access this
		AA = 'AA', _('Account Anniversary') #This will never appear as an option to users
		CE = 'CE', _('Community Event') #Network events are automatically set to community events
		NV = 'NV', _('Non-Volunteering Event')

		#Network events: CE, NV
		#Nonprofit events: CE, NV, VO
		#User events: CE, NV, NO

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
	attendees = models.ManyToManyField(User, blank = True, related_name="attendees")
	total_attending = models.IntegerField(default="0", validators=[MinValueValidator(0), MaxValueValidator(100)])

	parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="instances") #relates to itself

	class Meta: 
		ordering = ['-start_time']

	def __str__(self):
		return format(self.title)

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = create_token_event() #set the token on save
		return super(Event, self).save(*args, **kwargs)

'''class SignUp(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	sign_up_slots = models.IntegerField(help_text="What is the maximum number of people that will be at this event?", null = True, blank = True, validators=[MinValueValidator(1), MaxValueValidator(100)])
	attendees = models.ManyToManyField(User, blank = True, related_name="attendees")
	def __str__(self):
		return format(self.event + " sign up")'''