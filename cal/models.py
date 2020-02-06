from django.db import models
from django.utils import timezone
import datetime
from recurrence.fields import RecurrenceField

from accounts.models import User
from network.models import Network, Nonprofit

# Create your models here.
class Calendar(models.Model):
	title = models.CharField(help_text="What is the name of this calendar?", max_length=100, unique=True)

	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
	nonprofit = models.ForeignKey(Nonprofit, on_delete=models.CASCADE, null = True, blank = True)
	network = models.ForeignKey(Network, on_delete=models.CASCADE, null = True, blank = True)

	class Meta: 
		ordering = ['title']

	def __str__(self):
		return format(self.title)

class Event(models.Model):
	title = models.CharField(help_text="What is the name of the event?", max_length=75, default="")
	description = models.CharField(help_text='Describe the event briefly. What type of work will be done?', max_length=500, default="")

	start_time = models.DateTimeField('starting time', default=timezone.now)
	end_time = models.DateTimeField('ending time', default=timezone.now)
	all_day = models.BooleanField('all day?', help_text="will this event last the entire day", default=False)
	repeat = RecurrenceField()

	verified = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True, help_text="has a nonprofit representative verified this network?")

	calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, default="")#TODO: the default should be a global calendar

	class Meta: 
		ordering = ['title']

	def __str__(self):
		return format(self.title)