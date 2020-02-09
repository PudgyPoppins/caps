from django.db import models
from django.utils import timezone
import datetime
from recurrence.fields import RecurrenceField

from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.models import User
from network.models import Network, Nonprofit

# Create your models here.
class Calendar(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null = True, blank = True)
	nonprofit = models.OneToOneField(Nonprofit, on_delete=models.CASCADE, null = True, blank = True)
	network = models.OneToOneField(Network, on_delete=models.CASCADE, null = True, blank = True)

	network_calendar = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="networkcal") #network calendars consist of multiple nonprofit calendars, + their own events
	
	#should these next ones be cascade delete?
	user_calendar = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="usercal") #user calendars can consist of multiple network and nonprofit calendars, + their own events
	excluded_calendars = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="excludedcal") #users can choose to exclude certain nonprofit calendars from their user calendars

	isGlobal = models.BooleanField(default=False)

	def __str__(self):
		if(self.user):
			return format(self.user.username)
		elif(self.nonprofit):
			return format(self.nonprofit.slug)
		elif(self.network):
			return format(self.network.slug)
		else:
			return ("Global")

class Event(models.Model):
	title = models.CharField(help_text="What is the name of the event?", max_length=75, default="")
	description = models.CharField(help_text='Describe the event briefly. What type of work will be done?', max_length=500, default="")

	start_time = models.DateTimeField('starting time', default=timezone.now)
	end_time = models.DateTimeField('ending time', default=timezone.now)
	all_day = models.BooleanField('all day?', help_text="will this event last the entire day", default=False)
	repeat = RecurrenceField(null = True, blank = True)

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
		default=event_type_choices.NV,
	)

	sign_up_slots = models.IntegerField(help_text="What is the maximum number of people that will be at this event?", null = True, blank = True, validators=[MinValueValidator(1), MaxValueValidator(100)])
	attendees = models.ManyToManyField(User, blank = True, related_name="attendees")

	nonprofit_reps = models.ManyToManyField(User, 'nonreps', blank = True)
	verified = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True, help_text="has a nonprofit representative verified this network?")

	calendar = models.ManyToManyField(Calendar, default="")

	class Meta: 
		ordering = ['title']

	def __str__(self):
		return format(self.title)