import re

from django import template
register = template.Library()

@register.filter
def shorten_address(value):
	if value is not None:
		x = re.findall(r'^(?:.*?,){2}[^0-9]*', value)
		if x:
			newValue = x[0].rstrip()
			return newValue
		else:
			return value