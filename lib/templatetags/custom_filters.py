import re
import hashlib
import datetime

from django import template

from cal.models import Event
from accounts.models import User
from orgs.models import Goal

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
def int_percentage(value, arg):
	try:
		value = value.total_seconds() / 60 / 60
		arg = int(arg)
	except:
		try:
			value = int(value)
			arg = int(arg)
		except:
			return value

	return_val = int(value / arg * 100)
	if return_val > 100:
		return 100
	return return_val

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
	for cal in calendar.get_nested_calendars:
		for i in cal.event.all():
			relatives += get_all_relatives(i, relatives)
	relatives = list(set(relatives))
	return relatives

@register.filter
def humanize_duration(value):
	try:
		hours, remainder = divmod(value.total_seconds(), 3600)
		minutes, seconds = divmod(remainder, 60)
		human_format = []
		if hours:
			human_format.append(str(int(hours)) + " hours")
		if minutes:
			human_format.append(str(int(minutes)) + " minutes")
		if not(minutes or hours):
			human_format = ["0 minutes"]
		return ", ".join(human_format)
	except:
		return value

@register.filter
def javascriptize_duration(value):
	try:
		hours, remainder = divmod(value.total_seconds(), 3600)
		minutes, seconds = divmod(remainder, 60)
		return "%.2i:%.2i" % (hours, minutes)
	except:
		return value

@register.filter
def get(dictionary, key):
	try:
		#return humanize_duration(dictionary.get(key)) #go through this, if it's a duration it'll format it
		return dictionary.get(key)
	except:
		return None

'''
#Use:  
@register.filter
def filter(queryset, filter_value):
	try:
		keyword = filter_value.split("|")[0]
		value = filter_value.split("|")[1]

		custom_filter = {}
		custom_filter[keyword] = value
		return queryset.filter(**custom_filter)
	except:
		print("oh no!")
		return queryset'''