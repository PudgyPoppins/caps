def timezone(request):
	return {'tz': request.session.get('django_timezone')}