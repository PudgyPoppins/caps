from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView


from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
from network.models import Network, Nonprofit
from accounts.models import User
from orgs.models import Organization

from .models import *
from .forms import EventForm

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
	if org.public or (request.user.is_authenticated and request.user in org.member.all() or request.user in org.leader.all() or request.user in org.moderator.all()): #the organization is public or the user is a part of the organization
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
	return render(request, 'cal/cal/calendar_json.json', {"calendar" : calendar})

#Event Views
@login_required
def add_event_org(request, organization): #this is so that the computer doesn't get confused with adding an event to an org or to a network
	return HttpResponseRedirect(reverse('cal:add_event', kwargs={'organization': organization}))
@login_required
def add_event(request, username=None, nonprofit=None, network=None, organization=None):
	calendar = Calendar.objects.get(isGlobal=True)
	calendar_name = "the global calendar"
	success_url = reverse('home:main')
	if username:
		user = get_object_or_404(User, username=username)
		calendar = Calendar.objects.get(user=user)
		calendar_name = "your user calendar"
		success_url = reverse('accounts:get_profile')
	elif nonprofit and network:
		network = get_object_or_404(Network, slug=network)
		nonprofit = get_object_or_404(Nonprofit, slug=nonprofit, network=network)
		calendar = Calendar.objects.get(nonprofit=nonprofit)
		calendar_name = "the " + nonprofit.title + " nonprofit calendar"
		success_url = reverse('network:detailnon', kwargs={'network' : nonprofit.network.slug, 'slug' : nonprofit.slug})
	elif network:
		network = get_object_or_404(Network, slug=network)
		calendar = Calendar.objects.get(network=network)
		calendar_name = "the " + network.title + " network calendar"
		success_url = reverse('network:detail', kwargs={'slug' : network.slug})
	elif organization:
		organization = get_object_or_404(Organization, slug=organization)
		calendar = Calendar.objects.get(organization=organization)
		calendar_name = "the " + organization.title + " organization calendar"
		success_url = reverse('organization:detail', kwargs={'slug' : organization.slug})
	else:
		messages.error(request, "That wasn't a valid url for creating an event")
		raise Http404("Couldn't find this calendar")

	form = EventForm()
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
				return HttpResponseRedirect(success_url + "#calendar")
	return render(request, 'cal/event/event_form.html', {"form" : form, "c": calendar})

def event_detail(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]

	else:
		messages.error(request, "That event doesn't exist!")
		return HttpResponseRedirect(reverse('home:main'))
	return render(request, "cal/event/event_detail.html", {"event": event, 'c': event.calendar})

@login_required
def edit_event(request, token):
	event = Event.objects.filter(token=token)
	if event:
		event = event[0]

		if (event.created_by and event.created_by == request.user) or (event.calendar.nonprofit and request.user in event.calendar.nonprofit.nonprofit_reps.all()): #user permission to edit cases
			form = EventForm(instance = event)
			if request.method == "POST":
				form = EventForm(request.POST)
				if form.is_valid():
					event = form.save()
					if calendar.nonprofit and request.user in calendar.nonprofit.nonprofit_reps.all(): #automatically sets valid if the user is a nonprofit rep for that calendar
						event.verified = request.user
					event.save()
					messages.success(request, "Successfully added an event to %s!" %(calendar_name))
					#MAKE A FUNCTION ON EVENT MODEL THAT RETURNS ITS TYPE, AND ANOTHER ONE THAT RETURNS A SUCCESS URL FOR CREATION / EDIT
					#USE THAT FUNCTIONALITY ABOVE IN THE ADD_EVENT VIEW
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

@login_required
def event_sign_up(request, token):
	print("x")
