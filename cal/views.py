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

from .models import Calendar, Event
from .forms import EventForm

from rest_framework import viewsets
from rest_framework import permissions
from .serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-start_time')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]

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

#Event Views
@login_required
def add_event(request, username=None, nonprofit=None, network=None):
	calendar = Calendar.objects.get(isGlobal=True)
	success_url = reverse('home:main')
	if username:
		user = get_object_or_404(User, username=username)
		calendar = Calendar.objects.get(user=user)
		success_url = reverse('accounts:get_profile')
	elif nonprofit and network:
		network = get_object_or_404(Network, slug=network)
		nonprofit = get_object_or_404(Nonprofit, slug=nonprofit, network=network)
		calendar = Calendar.objects.get(nonprofit=nonprofit)
		success_url = reverse('network:detailnon', kwargs={'network' : nonprofit.network.slug, 'slug' : nonprofit.slug})
	elif network:
		network = get_object_or_404(Network, slug=network)
		print(network.slug)
		calendar = Calendar.objects.get(network=network)
		success_url = reverse('network:detail', kwargs={'slug' : network.slug})
	else:
		messages.error(request, "That wasn't a valid url for creating an event")
		raise Http404("Couldn't find this calendar")

	form = EventForm()
	if request.method == "POST":
			form = EventForm(request.POST)
			if form.is_valid():
				event = Event(form.cleaned_data)
				event.save()
				event.calendar.set([calendar])
				event.save()
				messages.success(request, "Event added successfully!")
				return HttpResponseRedirect(success_url + "#calendar")
	return render(request, 'cal/event/event_form.html', {"form" : form, "calendar": calendar})