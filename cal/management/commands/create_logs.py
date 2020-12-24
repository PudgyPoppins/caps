from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
import datetime, sys
from cal.models import Attendee, Event
from logs.models import Log

class Command(BaseCommand):
	help = 'Creates logs for completed attendees that don\'t current have logs created'

	def handle(self, *args, **kwargs):
		MAX_DESCRIPTION_LENGTH = Log._meta.get_field('description').max_length

		e_query = Event.objects.filter(Q(end_date__lt=datetime.datetime.today()) | Q(end_date=datetime.datetime.today(), end_time__lte=timezone.now()))
		e_query = [e for e in e_query if e.s_calendar.nonprofit]
		#^ get events that are done and have an assoicated nonprofit calendar
		a_query = Attendee.objects.filter(event__in=e_query, log__isnull=True, user__isnull=False) #get attendees who were at a completed event and who do not have logs
		if not a_query:
			self.stdout.write("All attendee events have logs created")
			sys.exit()
		for a in a_query:
			e = a.event
			np = e.s_calendar.nonprofit
			duration = e.end_datetime - e.start_datetime
			description_header = 'Automatically created log for the attended event "%s":\n' % e.s_title
			log = Log(
				attendee=a, 
				user=a.user, 
				nonprofit=np, 
				duration=duration, 
				start_date=e.start_date, 
				description=(description_header + e.s_description)[:MAX_DESCRIPTION_LENGTH]
			)
			log.save()
			self.stdout.write("Log created for attendee " + str(a) + ", event " + str(e.s_title))

'''
Cronjob
*/10 * * * * cd ~/Desktop/caps && source env/bin/activate && python3 manage.py create_logs
'''
