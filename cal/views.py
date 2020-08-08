from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import pytz
from dateutil.rrule import *
from datetime import datetime

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
from network.models import Network, Nonprofit
from accounts.models import User
from orgs.models import Organization

from .models import *
from .forms import EventForm, AttendeeForm

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

	form = EventForm() #EventFormNetwork
	if request.method == "POST":
		form = EventForm(request.POST)
		if form.is_valid():
			event = form.save()
			event.calendar = calendar
			event.created_by = request.user
			if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): #automatically sest valid if the user is a nonprofit rep for that calendar
				event.verified = request.user
			event.save()
			messages.success(request, "Successfully added an event to %s!" %(calendar_name))
			return HttpResponseRedirect(event.cal_url)
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
				d, context['d'] = request.GET['d'], request.GET['d']
				date = datetime.datetime.strptime(d, '%Y-%m-%d')
				if rrule.after(date, inc = True) != date:
					messages.error(request, "This event does not repeat on this date")
					return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))
				if len(ExcludedDates.objects.filter(date=date.date(), excluded=event)) > 0: #if date.date() in event.excluded_dates.all():
					print(date.date())
					try:
						event = Event.objects.filter(parent=event, start_time__gte=date, start_time__lt=date + datetime.timedelta(days=1))[0]
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

@login_required
def edit_event(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]

		if (event.created_by and event.created_by == request.user) or (event.calendar.nonprofit and request.user in event.calendar.nonprofit.nonprofit_reps.all()): 
		#user permission to edit cases
			form = EventForm(instance = event)
			if request.method == "POST":
				form = EventForm(request.POST)
				if form.is_valid():
					event = form.save()
					if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): 
					#automatically sets valid if the user is a nonprofit rep for that calendar
						event.verified = request.user
					event.save()
					messages.success(request, "Successfully added an event to %s!" %(calendar_name))
					return HttpResponseRedirect(event.cal_url)
		else:
			messages.error(request, "You don't have permission to edit this event!")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))

	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return render(request, "cal/event/event_update_form.html", {"form" : form, "event": event, 'c': event.calendar})

@login_required
def delete_event(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]
	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return render(request, "cal/event/event_update_form.html", {"event": event, 'c': event.calendar})

def event_sign_up(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]
		if event.rrule: #if it has an rrule, then it needs to be split
			try:
				d = request.GET['d']
				date = datetime.datetime.strptime(d, '%Y-%m-%d')
				rrule = rrulestr(event.rrule.replace('\\n', '\n'))
				if rrule.after(date, inc = True) != date:
					messages.error(request, "This event does not repeat on this date")
					return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : token}))
				
				date = pytz.utc.localize(date)
				#By this point, we've successfully confirmed that this date is valid for this event
				if len(Event.objects.filter(parent=event, start_time__gte=date, start_time__lte=date + datetime.timedelta(days=1))) >= 1:
					#This condition is met when the initial event was already split up on this date, so this just finds it again and sets it to that
					#Maybe the user is using an outdated link for their sign up or is just being cheeky; this makes sure that they don't unnecessarily create a new event
					event = Event.objects.filter(parent=event, start_time__gte=date, start_time__lt=date + datetime.timedelta(days=1))[0]
				else:
					if len(ExcludedDates.objects.filter(date=date.date())) >= 1:
						ed = ExcludedDates.objects.filter(date=date.date())[0]
					else:
						ed = ExcludedDates(date = date.date())
						ed.save()
					event.excluded_dates.add(ed)
					event.save()
					#^add this date instance as an excluded date
					event = Event(parent=event)
					event.start_time = event.parent.start_time.replace(year=date.year, month=date.month, day=date.day)
					event.save()
					event.end_time = event.start_time + (event.parent.end_time - event.parent.start_time)
					event.save()
					#create a new event with a new start_time and end_time
			except:
				messages.error(request, "You must sign up for this event on a specific date")
				return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
		#At this point, we either have a split event, or an event that didn't need splitting
		if (event.sign_up_slots is not None and event.attendee.count() < event.sign_up_slots) or (event.sign_up_slots is None and event.attendee.count() < event.parent.sign_up_slots):
			#this conditional confirms that there is enough sign up spaces left in the event
			if request.user.is_authenticated:
				if len(Attendee.objects.filter(user=request.user, event=event)) >= 1:
					messages.error(request, "You're already signed up for this event!")
				else:
					a = Attendee(user=request.user, event=event)
					a.save()
					messages.success(request, "You've successfully signed up for this event!")
				return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
				##^This code block is responsible for signing up the user for that event, or giving them an error
			else:
				form = AttendeeForm()
				if request.method == 'POST':
					form = AttendeeForm(request.POST)
					if form.is_valid():
						a = form.save(commit=False)
						a.event = event
						a.save()
						messages.success(request, "You've successfully signed up for this event!")
						return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
				return render(request, 'cal/event/sign_up.html', {'form': form, 'event': event})


		else:
			messages.error(request, "This event is already full! No sign up spaces left.")
			return HttpResponseRedirect(reverse('cal:eventdetail', kwargs={'token' : event.token}))
		#TODO: see if the event has enough spaces left for sign ups, see if the user is logged in, etc
	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return HttpResponse('bepis')


'''
* Verify that the event doesn't already have any children. If it does have children, then it's already been split before


* if the event is an rrule event, then get d, and add d to ExcludedDates
* Create a new event, with the parent as the original event, that has no rrule.
* If the user is logged in, search for an attendee for them, create a new one if it doesn't exist, and then add that attendee to the new event.
* If the user isn't logged in, give them a simple name form, then sign them up
'''