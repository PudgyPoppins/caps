from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_duration

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from network.models import Nonprofit
from accounts.models import User
from cal.models import Attendee
from orgs.models import create_token
# Create your models here.

def duration_validator(value): #you have to volunteer for AT LEAST 15 minutes
	if parse_duration(str(value))*60 < timedelta(minutes=15):
		raise ValidationError(
			_('duration must be greater than 15 minutes')
		)
class Log(models.Model):
	token = models.CharField(max_length=16, null=True, blank=True)
	verified = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_log') #pass the nonprofit rep through here
	processed = models.BooleanField(default=False)

	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='log')
	attendee = models.OneToOneField(Attendee, null=True, blank=True, on_delete=models.SET_NULL, related_name='log') #when your event is done, all of this info can be obtained through this
	nonprofit = models.ForeignKey(Nonprofit, null=True, blank=True, on_delete=models.SET_NULL, related_name='log')
	#nonprofit_text = models.CharField(max_length=128, null=True, blank=True) #in case they don't want to add a new nonprofit
	#^ I commented this out because I'm a greedy bastard that wants to make sure they add their nonprofits to the website, they can't just freeload with their text boxes!

	start_date = models.DateField(default=timezone.now)
	created_on = models.DateTimeField(default=timezone.now)
	duration = models.DurationField(default=0, validators=[duration_validator], help_text="How long you volunteered for (in the form HH:MM)")#you volunteer for some amount of hours

	description = models.CharField(max_length=512, help_text="A short description of the work that you completed. Can include who supervised you.", blank=True, null=True)

	def __str__(self):
		if self.user:
			return str(self.user) + " on " + self.start_date.strftime('%x')
		elif self.attendee:
			return str(self.attendee) + " on " + self.start_date.strftime('%x')
		else:
			return "log on " + self.start_date.strftime('%x')

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = create_token('logs', "Log") #set the token on save
		return super(Log, self).save(*args, **kwargs)

	@property
	def volunteer(self):
		if self.user:
			return str(self.user)
		elif self.attendee:
			return str(self.attendee)
		else:
			return "Anonymous Volunteer"