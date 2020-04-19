import re
import hashlib
import datetime

from django import template
register = template.Library()

@register.filter
def gravatar_url(email, size=40):
	default = "https://www.gravatar.com/avatar"

	m = hashlib.md5()
	m.update(email.lower().encode('utf-8'))
	email_hash = str(m.hexdigest())

	return "https://www.gravatar.com/avatar/" + str(email_hash) + "?d=retro&s=" + str(size)

@register.filter
def shorten_address(value):
	if value is not None:
		x = re.findall(r'^(?:.*?,){2}[^0-9]*', value)
		if x:
			newValue = x[0].rstrip()
			return newValue
		else:
			return value

@register.filter
def duration(start_time, end_time):
	duration = (end_time - start_time).total_seconds()
	hours, remainder = divmod(duration, 3600)
	minutes, seconds = divmod(remainder, 60)

	return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def multiply(value, arg):
    return value * arg
