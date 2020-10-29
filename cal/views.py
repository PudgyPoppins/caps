from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

import pytz
from dateutil.rrule import *
from datetime import datetime

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe

from django.forms.models import model_to_dict

# Create your views here.
from network.models import Network, Nonprofit
from accounts.models import User
from orgs.models import Organization

from .models import *
from .forms import EventForm, EventFormUpdate, EventFormNetwork, EventFormNetworkUpdate, AttendeeForm, RecurringEventForm

def index(request):
	return HttpResponse("This is where the global calendar would go.")

#Calendar views
def usercal(request, username):
	user = get_object_or_404(User, username=username)
	if request.user.is_authenticated and user == request.user:
		return HttpResponseRedirect(reverse('accounts:current_profile') + '#calendar')
	elif request.user.is_authenticated:
		messages.error(request, "You don't have permission to view this user's calendar!")
		return HttpResponseRedirect(reverse('accounts:current_profile') + '#calendar')
def redirect_usercal(request, username):
	return HttpResponseRedirect(reverse('cal:usercal', kwargs={'username' : username}))

def orgcal(request, organization):
	org = get_object_or_404(Organization, slug=organization)
	if org.public or (request.user.is_authenticated and request.user in org.member.all() or request.user in org.leader.all() or request.user in org.moderator.all()): 
	#the organization is public or the user is a part of the organization
		return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : org.slug}) + '#calendar')
	else: 
		messages.error(request, "You don't have permission to view this organization's calendar!")
		return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : org.slug}))
def redirect_orgcal(request, organization):
	return HttpResponseRedirect(reverse('cal:orgcal', kwargs={'organization' : organization}))

def networkcal(request, network):
	network = get_object_or_404(Network, slug=network)
	return HttpResponseRedirect(reverse('network:detail', kwargs={'slug' : network.slug}) + '#calendar')

def nonprofitcal(request, network, nonprofit):
	network = get_object_or_404(Network, slug=network)
	nonprofit = get_object_or_404(Nonprofit, slug=nonprofit, network=network)
	return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network' : nonprofit.network.slug, 'slug' : nonprofit.slug}) + '#calendar')

def calendar_json(request, token):
	calendar = Calendar.objects.filter(token=token)
	if calendar:
		calendar = calendar[0]
		if calendar.user and calendar.user != request.user:
			messages.error(request, "That calendar doesn't exist, or you don't have permission to see it!")
			return HttpResponseRedirect(reverse('home:main'))
	else:
		messages.error(request, "That calendar doesn't exist, or you don't have permission to see it!")
		return HttpResponseRedirect(reverse('home:main'))
	return render(request, 'cal/cal/calendar_json.json', {"calendar" : calendar}, content_type="application/json")

#Event Views
@login_required
def add_event_org(request, organization): #this is so that the computer doesn't get confused with adding an event to an org or to a network
	return HttpResponseRedirect(reverse('cal:add_event', kwargs={'organization': organization}))
@login_required
def add_event(request, username=None, nonprofit=None, network=None, organization=None):
	calendar = Calendar.objects.get(isGlobal=True)
	calendar_name = "the global calendar"
	if username:
		user = get_object_or_404(User, username=username)
		calendar = Calendar.objects.get(user=user)
		calendar_name = "your user calendar"
	elif nonprofit and network:
		network = get_object_or_404(Network, slug=network)
		nonprofit = get_object_or_404(Nonprofit, slug=nonprofit, network=network)
		if nonprofit.locked and not request.user in nonprofit.nonprofit_reps.all(): #if it's locked, and you're not a rep, you can't add an event
			messages.error(request, "A nonprofit representative has locked this nonprofit from user-created events")
			rep_link = reverse('network:representnon', kwargs={'network': network.slug, 'slug' : slug})
			messages.info(request, mark_safe("You don't have permission to perform this action! If you think that you should be able to lock this nonprofit, please fill out the <a href='%s'>form to represent this nonprofit</a>" %(rep_link)))
			return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network': network.slug, 'slug' : nonprofit.slug}))
		calendar = Calendar.objects.get(nonprofit=nonprofit)
		calendar_name = "the " + nonprofit.title + " nonprofit calendar"
	elif network:
		network = get_object_or_404(Network, slug=network)
		calendar = Calendar.objects.get(network=network)
		calendar_name = "the " + network.title + " network calendar"
	elif organization:
		organization = get_object_or_404(Organization, slug=organization)
		calendar = Calendar.objects.get(organization=organization)
		calendar_name = "the " + organization.title + " organization calendar"
	else:
		messages.error(request, "That wasn't a valid url for creating an event")
		raise Http404("Couldn't find this calendar")

	form = None #now it's global-er
	if network and not nonprofit:
		form = EventFormNetwork()
	else:
		form = EventForm()
	if request.method == "POST":
		if network and not nonprofit:
			form = EventFormNetwork(request.POST)
		else:
			form = EventForm(request.POST)
		if form.is_valid():
			event = form.save()
			event.calendar = calendar
			event.created_by = request.user
			if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): #automatically sest valid if the user is a nonprofit rep for that calendar
				event.verified = request.user
			event.save()
			messages.success(request, "Successfully added an event to %s!" %(calendar_name))
			return HttpResponseRedirect(event.s_calendar.cal_url)
	return render(request, 'cal/event/event_form.html', {"form" : form, "c": calendar})

def event_detail(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]
		context = {"event": event}
		context['c'] = event.s_calendar
		if event.rrule:

			rrule = rrulestr(event.rrule.replace('\\n', '\n'))
			next_repeat = str(rrule.after(datetime.datetime.now(), inc = True).date())
			context['next_repeat'] = next_repeat

			try:
				context['d'] = request.GET['d']
				date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d')
				if rrule.after(date, inc = True).date() != date.date():
					messages.error(request, "This event does not repeat on this date")
					return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))
				if len(ExcludedDates.objects.filter(date=date.date(), excluded=event)) > 0: #if date.date() in event.excluded_dates.all():
					try:
						event = Event.objects.filter(parent=event, start_date__gte=date, start_date__lt=date + datetime.timedelta(days=1))[0]
						return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
					except:
						messages.error(request, "This event does not repeat on this date")
						return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))
			except:
				context['d'] = None
		else:
			context['d'] = None
	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return render(request, "cal/event/event_detail.html", context)

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

def get_latest_until(event):
	eldest = get_eldest_event(event)
	relatives_empty = []
	relatives = get_all_relatives(eldest, relatives_empty)
	return_value = datetime.datetime(1, 1, 1)
	for i in relatives:
		if i.rrule:
			rrule = rrulestr(i.rrule.replace('\\n', '\n'))
			if rrule._until and rrule._until > return_value:
				return_value = rrule._until
	return return_value

def exclude_event_on_date(event, date):
	if isinstance(date, datetime.datetime):
		if len(ExcludedDates.objects.filter(date=date.date())) >= 1:
			ed = ExcludedDates.objects.filter(date=date.date())[0]
		else:
			ed = ExcludedDates(date = date.date())
			ed.save()
	else:
		if len(ExcludedDates.objects.filter(date=date)) >= 1:
			ed = ExcludedDates.objects.filter(date=date)[0]
		else:
			ed = ExcludedDates(date = date)
			ed.save()
	event.excluded_dates.add(ed)
	event.save()


@login_required
def edit_event(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]
		data = model_to_dict(event)
		calendar = event.s_calendar

		if not((event.s_created_by and event.s_created_by == request.user) or (event.calendar.nonprofit and request.user in event.calendar.nonprofit.nonprofit_reps.all())):
			#user permission to edit cases
			messages.error(request, "You don't have permission to edit this event!")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))

		if event.rrule and not request.GET.get('d'):
			messages.error(request, "You must delete this event on a specific date")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
		elif event.rrule and request.GET.get('d'):
			date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d').date()
			rrule = rrulestr(event.rrule.replace('\\n', '\n'))
			if rrule.after(datetime.datetime.combine(date, event.s_start_time), inc = True).date() != date:
				messages.error(request, "This event does not repeat on this date")
				return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))
		
		form = None #now it's global-er
		if calendar.network and not calendar.nonprofit:
			form = EventFormNetworkUpdate(instance = event, initial=data)
		else:
			form = EventFormUpdate(instance = event, initial=data)
		recurrence_form = RecurringEventForm()
		if request.method == "POST":

			block_list = ['created_by', 'verified', 'calendar', 'parent', 'excluded_dates'] #this data can't be set via a dictionary
			old_event_data = {key : val for key ,val in model_to_dict(event).items() if key not in block_list}#backup the old data
			restore_event = Event(created_by=event.created_by, verified=event.verified, calendar=event.calendar, parent=event.parent, **old_event_data)
			restore_event.excluded_dates.set(event.excluded_dates.all())
			#^create a restore_event to set the event back to after form.is_valid() messes it up

			if calendar.network and not calendar.nonprofit:
				form = EventFormNetworkUpdate(request.POST, instance = event, initial=data)
			else:
				form = EventFormUpdate(request.POST, instance = event, initial=data)

			if form.is_valid() and form.has_changed():
				event = restore_event
				if not event.parent and not event.instance.all() and not event.rrule:
					#Updating is simple for single-occurence, non-related events
					event = form.save()
					if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): 
					#automatically sets valid if the user is a nonprofit rep for that calendar
						event.verified = request.user
						event.save()
					messages.success(request, "Successfully update %s!" %(event.s_title))
					return HttpResponseRedirect(event.s_calendar.cal_url)
				recurrence_form = RecurringEventForm(request.POST)
				if recurrence_form.is_valid():
					#at this point, we have a recurring event that we'd like to do something with
					if recurrence_form.cleaned_data.get('change_type'):
						x = recurrence_form.cleaned_data.get('change_type') #one letter variable, easier to work with
						if x == "a":#update all events
							parent = get_eldest_event(event) #get the eldest event to plug into the relative finder
							for change in form.changed_data: #loop through the changed fields, and set the parent to them
								if change not in ['start_date', 'end_date']: #a recurring event where all of them start on the same date would be shit
									setattr(parent, change, form.cleaned_data.get(change))
							if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): #verify parent if possible
								parent.verified = request.user
							parent.save()
							relatives_empty = []
							relatives = get_all_relatives(parent, relatives_empty) #find all of the relatives including and below the parent level (so all of them)
							relatives.remove(parent) #remove the parent from this list
							for i in relatives:
								for change in form.changed_data:
									if change not in ['start_date', 'end_date']:
										setattr(i, change, None)#set all of the changed fields to None, so the children inherit from the parent
										i.save()	
							messages.success(request, "Successfully updated all events")
							return HttpResponseRedirect(parent.s_calendar.cal_url)

						elif x == "f": #update this event and all following ones
							date = datetime.date(1970, 1, 1)#we have to declare this variable first so it can be overwritten, just pick any date
							original_has_until = False
							original_has_attendees = False
							attendees = []

							if not event.rrule: #single instance event (that is still related, has a parent)
								date = event.start_date
								if event.attendee.all():
									original_has_attendees = True
									attendees += event.attendee.all()
									#save the attendees for later
								event_to_delete = event
								event = event.parent #set the event to the parent, it's easier to work with this change_type if it's on the rrule level
								event_to_delete.delete()#delete the current event, we'll replace it with an rrule event
							elif event.rrule: #if the initial event is an rrule, we need to get what day it's at and verify that it works
								date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d').date()
							rrule = rrulestr(event.rrule.replace('\\n', '\n'))
							if rrule._until:
								original_has_until = True #if it does have an until, then we need to find the furthest in the future until for later
								latest_until = get_latest_until(event)
							event.rrule = str(rrule.replace(until=date)).replace("\n", "\\n") #change the rrule until to the selected date, to make room for the new event
							if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): #verify event if possible
								event.verified = request.user
							event.save()
							relatives_empty = []
							relatives = get_all_relatives(event, relatives_empty) #do this up here so as not to include the new event in the search
							relatives.remove(event) #remove the event from this list

							new_event = Event(parent=event)#create a new event, this is the split part
							new_event.start_date = event.start_date.replace(year=date.year, month=date.month, day=date.day) #set the new start_date
							new_event.end_date = new_event.start_date + (event.end_datetime - event.start_datetime) #set the new end_date
							for change in form.changed_data: #loop through the changed fields, and set the new_event to them
								if change not in ['start_date', 'end_date']:#we don't really have a way to update these ones
									setattr(new_event, change, form.cleaned_data.get(change))
							if original_has_until:
								rrule = rrule.replace(until=latest_until) 
								#set the new rrule until to be the latest one, since this edits all events in the future, it will naturally have the latest until
							new_event.rrule = str(rrule.replace(dtstart=datetime.datetime.combine(date, event.s_start_time))).replace("\n", "\\n") 
							#set the new rrule to the old one, with a changed dtstart
							new_event.save()

							excluded_dates_set = []
							for i in Event.objects.filter(id__in=[i.id for i in relatives], start_date__gt=date):
								#go through the future children, and either delete unecessary rrules, or reset the changed fields and change the parent
								if i.rrule:
									for j in i.instance.all():
										j.parent = new_event
										j.save() #set all of the children to the new, updated event
									excluded_dates_set += i.excluded_dates.all()
									i.delete() #delete all rrules events that happen beyond this date
								else:
									i.parent = new_event
									i.save()
									for change in form.changed_data:
										if change not in ['start_date', 'end_date']:
											setattr(i, change, None)#set all of the changed fields to None, so the children inherit from the parent
											i.save()

							for i in event.excluded_dates.all():
								#loop through the excluded dates and give them to the new event if applicable
								if i.date > date:
									event.excluded_dates.remove(i)
									event.save()
									new_event.excluded_dates.add(i)
									new_event.save()
							for i in excluded_dates_set:
								#loop through the second set of excluded dates to catch all of the rrule events
								if i.date > date:
									new_event.excluded_dates.add(i)
									new_event.save()

							if original_has_attendees:
								#split the event, create a new one, 
								exclude_event_on_date(new_event, date)
								new_event = Event(parent=new_event, start_date=new_event.start_date, end_date = new_event.end_date)
								new_event.save()
								for i in attendees:
									i.event = new_event #set the event to the new one
									i.save()
								new_event.attendee.set(attendees)
								new_event.save()
								#override new_event variable with an even newer event, this time with attendees

							messages.success(request, "Successfully updated this and following events")
							return HttpResponseRedirect(new_event.s_calendar.cal_url)


						else: #update just this event
							if event.rrule: #rrule events have to be split
								date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d')
								exclude_event_on_date(event, date)

								event = Event(parent=event) #start overwriting the event to the new one
								event.start_date = event.parent.start_date.replace(year=date.year, month=date.month, day=date.day)
								event.end_date = event.start_date + (event.parent.end_datetime - event.parent.start_datetime)
								event.save()
							
							for change in form.changed_data: #loop through the changed fields, and set the event to them
								setattr(event, change, form.cleaned_data.get(change))
							event.save()

							messages.success(request, "Successfully updated event")
							return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token})) 
							#send the user back to the specific event they just changed
					else:
						messages.error(request, "An error occured. Try refreshing your browser?")
			else:
				messages.error(request, "Your event couldn't be updated. Did you make sure that you changed the field you were looking to update?")


	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return render(request, "cal/event/event_update_form.html", {"form" : form, "event": event, 'c': event.s_calendar})

@login_required
def delete_event(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]
	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))

	if not((event.s_created_by and event.s_created_by == request.user) or (event.calendar.nonprofit and request.user in event.calendar.nonprofit.nonprofit_reps.all())):
		messages.error(request, "You do not have permission to delete this event")
		return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))

	if event.rrule and not request.GET.get('d'):
		messages.error(request, "You must delete this event on a specific date")
		return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
	elif event.rrule and request.GET.get('d'):
		date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d').date()
		rrule = rrulestr(event.rrule.replace('\\n', '\n'))
		if rrule.after(datetime.datetime.combine(date, event.s_start_time), inc = True).date() != date:
			messages.error(request, "This event does not repeat on this date")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))

	form = RecurringEventForm()
	if request.method == 'POST':
		cal_url = event.s_calendar.cal_url #save it here before we delete the event
		if not event.parent and not event.instance.all() and not event.rrule:
			#Deletion is simple for single-occurence, non-related events
			event.delete()
			messages.success(request, "Successfully deleted event")
			return HttpResponseRedirect(cal_url)
		form = RecurringEventForm(request.POST)
		if form.is_valid():
			#at this point, we have a recurring event that we'd like to do something with
			if form.cleaned_data.get('change_type'):
				x = form.cleaned_data.get('change_type') #one letter variable, easier to work with
				if x == "a":#delete all events
					parent = get_eldest_event(event) #get the eldest event to plug into the relative finder
					relatives_empty = []
					relatives = get_all_relatives(parent, relatives_empty) #find all of the relatives including and below the parent level (so all of them)
					for i in relatives:
						i.delete() #delete them all
					messages.success(request, "Successfully deleted all events")
					return HttpResponseRedirect(cal_url)

				elif x == "f":#delete this event and all following ones
					date = datetime.date(1970, 1, 1)#we have to declare this variable first so it can be overwritten, just pick any date
					if not event.rrule: #single instance event (that is still related, has a parent)
						date = event.start_date
						event = event.parent #set the event to the parent, it's easier to work with this change_type if it's on the rrule level
					elif event.rrule: #if the initial event is an rrule, we need to get what day it's at and verify that it works
						date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d').date()
					#at this point we have an rrule event to work with, and a date
					rrule = rrulestr(event.rrule.replace('\\n', '\n'))
					event.rrule = str(rrule.replace(until=date)).replace("\n", "\\n") #change the rrule until to the selected date, effictively "deleting" it.
					event.save()
					relatives_empty = []
					relatives = get_all_relatives(event, relatives_empty)
					for i in Event.objects.filter(id__in=[i.id for i in relatives], start_date__gte=date):
						i.delete()
						# delete all of the children, and the event itself if it starts on the same date
					messages.success(request, "Successfully deleted event")
					return HttpResponseRedirect(cal_url)


				else:#delete just this event, the default option if something screws up with the change_type
					if event.rrule: #rrule events get "deleted" on certain days by adding an Excluded Date
						try:
							date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d')
							exclude_event_on_date(event, date)
							messages.success(request, "Successfully deleted event")
							return HttpResponseRedirect(event.s_calendar.cal_url)
						except:
							messages.error(request, "You must delete this event on a specific date")
							return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
					else:
						event.delete() #no rrule means it already was a single instance, just delete it
						messages.success(request, "Successfully deleted event")
						return HttpResponseRedirect(cal_url)
			else:
				messages.error(request, "An error occured. Try refreshing your browser?")
	return render(request, "cal/event/event_confirm_delete.html", {"event": event, 'c': event.calendar, 'form': form})

def event_sign_up(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]
		if event.rrule: #if it has an rrule, then it needs to be split
			try:
				date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d')
				rrule = rrulestr(event.rrule.replace('\\n', '\n'))
				if rrule.after(date, inc = True).date() != date.date():
					messages.error(request, "This event does not repeat on this date")
					return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))
				
				#date = pytz.utc.localize(date)
				#By this point, we've successfully confirmed that this date is valid for this event
				if len(Event.objects.filter(parent=event, start_date__gte=date, start_date__lte=date + datetime.timedelta(days=1))) >= 1:
					#This condition is met when the initial event was already split up on this date, so this just finds it again and sets it to that
					#Maybe the user is using an outdated link for their sign up or is just being cheeky; this makes sure that they don't unnecessarily create a new event
					event = Event.objects.filter(parent=event, start_date__gte=date, start_date__lt=date + datetime.timedelta(days=1))[0]
				else:
					#if it wasn't split up already, then do that here
					exclude_event_on_date(event, date)
					#^add this date instance as an excluded date
					event = Event(parent=event) #start overwriting the event to the new one
					event.start_date = event.parent.start_date.replace(year=date.year, month=date.month, day=date.day)
					event.end_date = event.start_date + (event.parent.end_datetime - event.parent.start_datetime)
					event.save()
					#^create a new event with a new start_date and end_date
			except:
				messages.error(request, "You must sign up for this event on a specific date")
				return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
		#At this point, we either have a split event, or an event that didn't need splitting
		if event.start_datetime < timezone.now():
			messages.error(request, "You can't sign up for a past event!")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
		if event.s_sign_up_slots is not None and event.attendee.count() < event.s_sign_up_slots:
			#this conditional confirms that there is enough sign up spaces left in the event
			if request.user.is_authenticated:
				if len(Attendee.objects.filter(user=request.user, event=event)) >= 1:
					messages.info(request, "You're already signed up for this event!")
					#^even though they're already signed up personally, let them sign someone else up, like a friend
					form = AttendeeForm()
					if request.method == 'POST':
						form = AttendeeForm(request.POST)
						if form.is_valid():
							a = form.save(commit=False)
							a.event = event
							a.save()
							send_confirmation_email(a)
							messages.success(request, "You've successfully signed up for this event! Check your email for a verification message.")
							return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
					return render(request, 'cal/event/sign_up.html', {'form': form, 'event': event})
				else:
					#automatically sign them up if they're logged in
					a = Attendee(user=request.user, email=request.user.email, event=event)
					a.save()
					send_confirmation_email(a)
					messages.success(request, "You've successfully signed up for this event! Check your email for a verification message.")
				return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
				##^This code block is responsible for signing up the user for that event, or giving them an error
			else:
				#give 'em the form if they're not signed in
				form = AttendeeForm()
				if request.method == 'POST':
					form = AttendeeForm(request.POST)
					if form.is_valid():
						a = form.save(commit=False)
						a.event = event
						a.save()
						send_confirmation_email(a)
						messages.success(request, "You've successfully signed up for this event! Check your email for a verification message.")
						return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
				return render(request, 'cal/event/sign_up.html', {'form': form, 'event': event})

		elif event.s_sign_up_slots is None or event.s_sign_up_slots == 0:
			messages.error(request, "This event doesn't allow sign up spaces.")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
		else:
			messages.error(request, "This event is already full! No sign up spaces left.")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return HttpResponse('bepis')

def send_confirmation_email(a):
	send_mail(
		'Confirming your event sign up',
		render_to_string('cal/snippets/attendee_email.txt', {'attendee': a, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
		'pudgypoppins@gmail.com',
		[a.s_email],
		html_message=render_to_string('cal/snippets/attendee_email.html', {'attendee': a, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
	)

def unattend(request, uuid):
	attendee = Attendee.objects.filter(uuid=uuid)
	if attendee:
		attendee = attendee[0]
		event = attendee.event
		if event.start_datetime < timezone.now():
			attendee.delete()
			messages.success(request, "Successfully unattended event")
		else:
			messages.error(request, "That event already happened! You can't unattend now!")
		return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
	else:
		messages.error(request, "That attendee doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))

'''
* Verify that the event doesn't already have any children. If it does have children, then it's already been split before


* if the event is an rrule event, then get d, and add d to ExcludedDates
* Create a new event, with the parent as the original event, that has no rrule.
* If the user is logged in, search for an attendee for them, create a new one if it doesn't exist, and then add that attendee to the new event.
* If the user isn't logged in, give them a simple name form, then sign them up
'''

@login_required
def calendar_subscribe(request, token):
	calendar = Calendar.objects.filter(token=token)
	if calendar:
		calendar = calendar[0]
		user = request.user
		u_cal = user.calendar
		if u_cal == calendar or calendar.user:
			messages.error(request, "You can't subscribe to a user calendar")
			return HttpResponseRedirect(calendar.cal_url)
		if calendar in u_cal.get_nested_calendars:
			messages.info(request, "You're already subscribed to this calendar")
		else:
			if calendar in u_cal.excludedcal.all():
				u_cal.excludedcal.remove(calendar)
			u_cal.calendars.add(calendar)
			u_cal.save()
			messages.success(request, "Successfully subscribed to this calendar")
		return HttpResponseRedirect(calendar.cal_url)
	else:
		messages.error(request, "That calendar doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))

@login_required
def calendar_unsubscribe(request, token):
	calendar = Calendar.objects.filter(token=token)
	if calendar:
		calendar = calendar[0]
		user = request.user
		u_cal = user.calendar
		if u_cal == calendar:
			messages.error(request, "You can't unsubscribe from your own calendar!")
			return HttpResponseRedirect(calendar.cal_url)
		if calendar in u_cal.get_nested_calendars:
			if calendar in u_cal.calendars.all():
				u_cal.calendars.remove(calendar)
				messages.success(request, "Successfully unsubscribed from to this calendar")
			elif calendar not in u_cal.excludedcal.all():
				u_cal.excludedcal.add(calendar)
				messages.success(request, "Successfully unsubscribed from to this calendar")
			else: #the only other possibility is that it's already in excludedcal.all()
				messages.info(request, "You're already unsubscribed to this calendar")
			return HttpResponseRedirect(calendar.cal_url)
		else:
			#you're only subscribed to a calendar if you're explicitly subscribed to it (it's in calendars.all()), or if you're implicitly subscribed to it (it's a child of something in calendars.all())
			messages.info(request, "You're not subscribed to this calendar in the first place")
			return HttpResponseRedirect(calendar.cal_url)
	else:
		messages.error(request, "That calendar doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))