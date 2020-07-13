from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

# Register your models here.
from .models import *
from .forms import CalendarAdminForm, EventAdminForm

class NotNullFilter(admin.SimpleListFilter):
	title = 'Filter title not set'
	parameter_name = 'parameter name not set'

	def lookups(self, request, model_admin):
		return (
			('not_null', 'Not empty only'),
			('null', 'Empty only'),
		)

	def queryset(self, request, queryset):
		filter_string = self.parameter_name + '__isnull'
		if self.value() == 'not_null':
			is_null_false = {
				filter_string: False
			}
			return queryset.filter(**is_null_false)

		if self.value() == 'null':
			is_null_true = {
				filter_string: True
			}
			return queryset.filter(**is_null_true)

class UserFilter(NotNullFilter):
	title = "User"
	parameter_name = "user"
class OrganizationFilter(NotNullFilter):
	title = "Organization"
	parameter_name = "organization"
class NonprofitFilter(NotNullFilter):
	title = "Nonprofit"
	parameter_name = "nonprofit"
class NetworkFilter(NotNullFilter):
	title = "Network"
	parameter_name = "network"

class EventInline(admin.TabularInline):
	model = Event
	extra = 1

class CalendarAdmin(admin.ModelAdmin):
	#inlines = [EventInline,]
	list_filter = (UserFilter, OrganizationFilter, NonprofitFilter, NetworkFilter)
	form = CalendarAdminForm
	list_display = ('token', 'user', 'organization', 'nonprofit', 'network', 'isGlobal')
	search_fields = ('user', 'organization', 'nonprofit', 'network')

class EventAdmin(admin.ModelAdmin):
	form = EventAdminForm
	list_display = ('title', 'token', 'calendar', 'start_time', 'end_time', 'rrule')
	search_fields = ['title']

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)