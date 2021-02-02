import pytz

from django.utils import timezone

class TimezoneMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		try:
			tzname = request.session.get('django_timezone')
			# get the timezone name from the cookie django_timezone
			if tzname:
				timezone.activate(pytz.timezone(tzname))
			else:
				#timezone.deactivate()
				#if it doesn't exist just set it to Mountain time
				request.session['django_timezone'] = "US/Mountain"
				timezone.activate('US/Mountain')
		except:
			timezone.activate('US/Mountain')
		return self.get_response(request)
