from django.contrib import admin

# Register your models here.
from .models import *
from django.forms import CheckboxSelectMultiple

class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class CalendarAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    #list_filter = ['flagged', 'pub_date']
    #list_display = ('title', 'pub_date', 'was_flagged', 'slug')
    #search_fields = ['title']

class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'start_time', 'end_time', 'repeat')
	list_filter = ['title']
	search_fields = ['title']

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)