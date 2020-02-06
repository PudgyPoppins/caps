from django.contrib import admin

# Register your models here.
from .models import *
from .forms import CalendarAdminForm

class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class CalendarAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    #list_filter = ['flagged', 'pub_date']
    form = CalendarAdminForm
    list_display = ('title', 'user', 'nonprofit', 'network')
    search_fields = ('title', 'user', 'nonprofit', 'network')

class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'calendar', 'start_time', 'end_time', 'repeat')
	search_fields = ['title']

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)