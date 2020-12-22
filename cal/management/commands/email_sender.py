from django.core.management.base import BaseCommand
from django.utils import timezone
from cal.models import *

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends emails to the attendees of events happening within the next 30 minutes'

    def handle(self, *args, **kwargs):
        thirty_mins_later = timezone.now() + datetime.timedelta(minutes=30)
        e_query = Event.objects.filter(start_date = datetime.datetime.today(), start_time__gte=timezone.now(), start_time__lte=thirty_mins_later)
        for e in e_query:
            for a in e.attendee.all():
                if not a.notified:
                    send_mail(
                        "You're volunteering soon!",
                        render_to_string('cal/snippets/attendee_email.txt', {'attendee': a, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME, 'second_notif': True}),
                        settings.EMAIL_HOST_USER,
                        [a.s_email],
                        html_message=render_to_string('cal/snippets/attendee_email.html', {'attendee': a, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME, 'second_notif': True}),
                    )
                    a.notified = True
                    a.save()
                    self.stdout.write("Email sent to " + str(a))

'''
Cronjob
*/10 * * * * cd ~/Desktop/caps && source env/bin/activate && python3 manage.py email_sender
'''
