from django.db import models
from django.utils import timezone
import datetime
from recurrence.fields import RecurrenceField

from accounts.models import User
from network.models import Network, Nonprofit

# Create your models here.
class Calendar(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
	nonprofit = models.ForeignKey(Nonprofit, on_delete=models.CASCADE, null = True, blank = True)
	network = models.ForeignKey(Network, on_delete=models.CASCADE, null = True, blank = True)

class Event(models.Model):
	title = models.CharField('What is the name of the event?', max_length=75, default="")
	description = models.CharField('Describe the event briefly. What type of work will be done?', max_length=500, default="")

	start_time = models.DateTimeField('starting time', default=timezone.now)
	end_time = models.DateTimeField('ending time', default=timezone.now)
	all_day = models.BooleanField('will this event last the entire day', default=False)
	repeat = RecurrenceField()
	end_repeat = models.DateTimeField('end repeat date', default=timezone.now() + datetime.timedelta(days=365))#default end repeat to a year after today

	calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)