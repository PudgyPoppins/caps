from django.contrib import admin

# Register your models here.
from .models import *

class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class CalendarAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    #list_filter = ['flagged', 'pub_date']
    list_display = ('title', 'user', 'nonprofit', 'network')
    #search_fields = ['title']

class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'calendar', 'start_time', 'end_time', 'repeat')
	list_filter = ['title']
	search_fields = ['title']

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)