from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView


from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.
from network.models import Network, Nonprofit
from accounts.models import User

from .models import Calendar, Event
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

def networkcal(request, network):
	network = get_object_or_404(Network, slug=network)
	return HttpResponseRedirect(reverse('network:detail', kwargs={'slug' : network.slug}) + '#calendar')

def nonprofitcal(request, network, nonprofit):
	network = get_object_or_404(Network, slug=network)
	nonprofit = get_object_or_404(Nonprofit, slug=nonprofit, network=network)
	return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network' : nonprofit.network.slug, 'slug' : nonprofit.slug}) + '#calendar')

#Event Views
class AddEventView(LoginRequiredMixin, CreateView):
	model = Event
	#fields = ['title', 'src_link', 'src_file']
	form_class = EventForm
	def get_success_url(self):
		if self.object.calendar.nonprofit:
			return reverse('nonprofit:detail', kwargs={'network' : self.object.calendar.nonprofit.network.slug, 'slug' : self.object.calendar.nonprofit.slug})
		else:
			return reverse('home:main')
	template_name = 'cal/event/event_form.html'
	def form_valid(self, form):
		form.instance.created_by = self.request.user #sets the created_by user to the current one
		return super().form_valid(form)
