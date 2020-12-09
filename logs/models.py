from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_duration

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from network.models import Nonprofit
from accounts.models import User
from cal.models import Attendee
# Create your models here.

def duration_validator(value): #you have to volunteer for AT LEAST 15 minutes
	if parse_duration(str(value))*60 < timedelta(minutes=15):
		raise ValidationError(
			_('duration must be greater than 15 minutes')
		)
class Log(models.Model):
	verified = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_log') #pass the nonprofit rep through here

	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='log')
	attendee = models.ForeignKey(Attendee, null=True, blank=True, on_delete=models.SET_NULL) #when your event is done, all of this info can be obtained through this
	nonprofit = models.ForeignKey(Nonprofit, null=True, blank=True, on_delete=models.SET_NULL)

	start_date = models.DateField(default=timezone.now)
	created_on = models.DateField(default=timezone.now)
	duration = models.DurationField(default=0, validators=[duration_validator], help_text="How long you volunteered for (in the form HH:MM)")#you volunteer for some amount of hours

	description = models.CharField(max_length=512, help_text="A short description of the work that you completed. Can include who supervised you.", blank=True, null=True)

	def __str__(self):
		if self.user:
			return str(self.user) + " log on " + str(self.start_date)