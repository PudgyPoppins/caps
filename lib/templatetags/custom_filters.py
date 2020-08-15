import re
import hashlib
import datetime

from django import template

from cal.models import Event

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


@register.filter
def getLongDate(value):
	try:
		long_date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
		long_date_str = long_date.strftime('%b %-d, %Y')
		return long_date_str
	except:
		return value

@register.filter
def rruleExdate(value, event):
	dates = event.excluded_dates.all()
	if len(dates) > 0:
		if value.find("EXDATE:") != -1: #there already is a valid EXDATE, let's insert this right after it
			empty = ""
			for i in range(len(dates)):
				empty += str(dates[i]) + "T" + event.s_start_time.strftime("%H%M00") + ","
			x = value[:value.find("EXDATE:")] + empty + value[value.find("EXDATE:"):]
		else: #there is no EXDATE, let's create one
			value += "\\" + "nEXDATE:" #hacky way to add string without newline
			for i in range(len(dates)):
				value += str(dates[i]) + "T" + event.s_start_time.strftime("%H%M00")
				if i != len(dates) - 1:
					value += ","
			x = value
	else:
		x = value
	return x

def get_eldest_event(event):
	#gets the "eldest" event, the original
	if event.parent:
		get_eldest_event(event.parent)
	else:
		return event
	return get_eldest_event(event.parent)
def get_all_relatives(event, relatives):
	#returns all lower relative events (and itself)
	relatives.append(event)
	for i in event.instance.all():
		relatives.append(i)
		get_all_relatives(i, relatives)
	relatives = list(set(relatives))
	return relatives

@register.filter
def get_calendar_events(calendar):
	relatives = []
	empty_relatives = []
	if calendar.networkcal.all():
		for noncal in calendar.networkcal.all():
			for i in noncal.event.all():
				relatives += get_all_relatives(i, empty_relatives)
	if calendar.event.all():
		for i in calendar.event.all():
			relatives += get_all_relatives(i, empty_relatives)
	relatives = list(set(relatives))
	return relatives

'''@register.filter
def get_relatives(event):
	relatives = get_all_relatives(event, empty_relatives)
	print(relatives)
	return relatives'''