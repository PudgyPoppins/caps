from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView


from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.safestring import mark_safe

from django.core.mail import mail_admins
from django.conf import settings

# Create your views here.
from django.db.models import Q
from cal.models import Calendar
from orgs.models import TextPost

from .models import Network, Nonprofit
from .forms import *
from lib.forms import CreateAnnouncement, ReplyAnnouncement

class IndexView(generic.ListView):
	template_name = 'network/index.html'
	context_object_name = 'network_list'

	def get_queryset(self):
		"""Return networks filtered by most recent (and not in the future)"""
		return Network.objects.filter(
			pub_date__lte=timezone.now()
		).order_by('-pub_date')#[:5] uncomment this to show only most recent 5

def search(request):
	non_query = request.GET.get('nonprofit', None)
	net_query = request.GET.get('network', None)
	id_query = request.GET.get('id', None)
	results = []
	if not non_query is None:
		results = Nonprofit.objects.filter(Q(title__icontains=non_query) | Q(network__title__icontains=non_query)).distinct()
	elif not net_query is None:
		results = Network.objects.filter(title__icontains=net_query)
	elif not id_query is None:
		results = Nonprofit.objects.filter(id=id_query)
	response = {}
	for i in results:
		if not net_query: response[i.id] = {"title":i.title, "location":i.network.title, "has_reps": bool(i.nonprofit_reps.all()), "url": i.get_absolute_url()}
		else: response[i.id] = {"title":i.title}
	return JsonResponse(response)

class AddNetView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
	model = Network
	#fields = ['title', 'src_link', 'src_file']
	form_class = NetworkForm
	success_url = reverse_lazy('network:index')
	template_name = 'network/net/network_form.html'
	success_message = "%(title)s was created successfully"
	def form_valid(self, form):
		form.instance.created_by = self.request.user #sets the created_by user to the current one

		network = form.save(commit=False)
		network.save() #saves the object, sets the id
		self.object = network

		network_cal = Calendar(network=self.object)
		network_cal.save()

		messages.success(self.request, self.get_success_message())
		return HttpResponseRedirect(self.get_success_url())

class DeleteNetView(LoginRequiredMixin, DeleteView):
	model = Network
	success_url = reverse_lazy('network:index')
	template_name = 'network/net/network_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (self.object.created_by == request.user or request.user.has_perm('network.delete_network')) #return whether or not the current user created this object, or if they have explicit permission to delete networks
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to delete this network!")
			return HttpResponseRedirect(reverse('network:detail', kwargs={'slug' : self.object.slug}))
		return super(DeleteNetView, self).dispatch(request, *args, **kwargs)

class UpdateNetView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
	model = Network
	form_class = NetworkForm
	template_name = 'network/net/network_update_form.html'
	success_message = "%(title)s was updated successfully"
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.slug})


class NetDetailView(generic.DetailView):
	model = Network
	template_name = 'network/net/network_detail.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['is_on_detail_page'] = True
		context['calendar'] = Calendar.objects.get(network=self.object.id)
		context['reasons'] = ["General trolling", "The network name is not accurate / inappropiate", "The network image is not accurate / inappropiate", "The coordinates are wrong"]
		return context


class AddNonView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
	model = Nonprofit
	form_class = NonprofitFormCreate
	template_name = 'network/non/nonprofit_form.html'
	success_message = "%(title)s was created successfully"
	def get_form_class(self):
		if self.kwargs.get('network'):
			return NonprofitFormCreate
		else: #no network specified
			return NonprofitFormUpdate
	def get_success_url(self):
		return reverse('network:detailnon', kwargs={'network': self.object.network.slug, 'slug' : self.object.slug})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.kwargs.get('network'):
			context['network'] = get_object_or_404(Network, slug=self.kwargs['network'])#pass the network data to the createview so it can use it for coords and stuff
		return context
	def form_valid(self, form):
		form.instance.created_by = self.request.user
		nonprofit = form.save(commit=False)
		if self.kwargs.get('network'):
			nonprofit.network = get_object_or_404(Network, slug=self.kwargs['network'])
		tag_temp_var = form.cleaned_data.get('tags') #this gets the tag data
		nonprofit.save() #saves the object, sets the id

		nonprofit.tags.set(tag_temp_var) #saves the previous tag data after the id is created
		nonprofit.save()
		self.object = nonprofit

		network_calendar = Calendar.objects.get(network=self.object.network.id)
		nonprofit_cal = Calendar(nonprofit=self.object, network_calendar=network_calendar)
		nonprofit_cal.save() #these last three lines create a calendar for this nonprofit

		messages.success(self.request, self.get_success_message())
		return HttpResponseRedirect(self.get_success_url())
	

class UpdateNonView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
	model = Nonprofit
	form_class = NonprofitFormUpdate
	template_name = 'network/non/nonprofit_update_form.html'
	success_message = "%(title)s was updated successfully"
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['network'] = get_object_or_404(Network, slug=self.kwargs['network'])#pass the network data to the updateview so it can use it for coords and stuff
		return context

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (not self.object.locked or request.user in self.object.nonprofit_reps.all() or request.user.is_staff) #if it's not locked, or you're a rep, or an admin, return true
		return False
	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "This nonprofit is locked for updates!")
			return HttpResponseRedirect(self.get_success_url())
		return super(UpdateNonView, self).dispatch(request, *args, **kwargs)

class DeleteNonView(LoginRequiredMixin, DeleteView):
	model = Nonprofit
	success_url = reverse_lazy('network:index')
	template_name = 'network/non/nonprofit_confirm_delete.html'
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
	
	def user_passes_test(self, request): #if there's a rep, you can only delete it if you're a rep or admin. Else, you can only delete if you created it or are admin
		if request.user.is_authenticated:
			self.object = self.get_object()
			if self.object.nonprofit_reps.all():
				return (request.user in self.object.nonprofit_reps.all() or request.user.is_staff)
			else:
				return (self.object.created_by == request.user or request.user.is_staff)
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to delete this nonprofit!")
			return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network': self.object.network.slug, 'slug' : self.object.slug}))
		return super(DeleteNonView, self).dispatch(request, *args, **kwargs)

class NonDetailView(generic.DetailView):
	model = Nonprofit
	template_name = 'network/non/nonprofit_detail.html'
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['calendar'] = Calendar.objects.get(nonprofit=self.object.id)
		form = CreateAnnouncement()
		context['form'] = form
		return context

def non_represent(request, network, slug):
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network__slug=network)
	form = NonprofitFormRepresent()
	if request.method == 'POST':
		form = NonprofitFormRepresent(request.POST, request.FILES)
		if form.is_valid() and request.user.is_authenticated and request.user not in nonprofit.nonprofit_reps.all():
			rep = form.save(commit=False)
			rep.user = request.user
			rep.nonprofit = nonprofit
			rep.save()
			messages.success(request, "Your application has been submitted and is currently under review. We will contact you when this process is complete.")
			html = "<p>A new nonprofit application for " + str(rep.user) + " has been created, who is applying for " + rep.nonprofit.title + ". Check the admin site to see more.</p>"
			mail_admins(subject = 'New nonprofit application',  message = 'A new nonprofit application has been created', fail_silently=True, html_message = html)
			return HttpResponseRedirect(nonprofit.get_absolute_url())
		elif request.user in nonprofit.nonprofit_reps.all():
			messages.error(request, "You're already representing this nonprofit!")
		else:
			messages.error(request, "You have to be logged in to submit this form!")
		return HttpResponseRedirect(nonprofit.get_absolute_url())
	context = {
		'form': form,
		'nonprofit': nonprofit,
		'site': settings.SITE_NAME,
		'email': settings.ADMINS[0][1]
	}
	return render(request, 'network/non/nonprofit_rep_form.html', context)

@login_required
def non_unrepresent(request, network, slug):
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network__slug=network)
	if request.user in nonprofit.nonprofit_reps.all():
		nonprofit.nonprofit_reps.remove(request.user)
		nonprofit.save()
		messages.success(request, "Successsfully unlocked this nonprofit, allowing edits and event creations by regular users")
	else:
		messages.error(request, "You aren't a nonprofit representative!")
	return HttpResponseRedirect(nonprofit.get_absolute_url())

@login_required
def non_lock(request, network, slug):
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network__slug=network)
	if request.user in nonprofit.nonprofit_reps.all() or request.user.is_staff:
		nonprofit.locked = True
		nonprofit.save()
		messages.success(request, "Successsfully locked this nonprofit from edits and event creations by regular users")
	else:
		rep_link = reverse('network:representnon', kwargs={'network': network, 'slug' : slug})
		messages.error(request, mark_safe("You don't have permission to perform this action! If you think that you should be able to lock this nonprofit, please fill out the <a href='%s'>form to represent this nonprofit</a>" %(rep_link)))
	return HttpResponseRedirect(nonprofit.get_absolute_url())

@login_required
def non_unlock(request, network, slug):
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network__slug=network)
	if request.user in nonprofit.nonprofit_reps.all() or request.user.is_staff:
		nonprofit.locked = False
		nonprofit.save()
		messages.success(request, "Successsfully unlocked this nonprofit, allowing edits and event creations by regular users")
	else:
		messages.error(request, "You don't have permission to perform this action!")
	return HttpResponseRedirect(nonprofit.get_absolute_url())

@login_required
def view_logs(request, network, slug):
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network__slug=network)
	if request.user in nonprofit.nonprofit_reps.all() or request.user.is_staff:
		log_array = []
		for i in list(dict.fromkeys([i.start_date for i in nonprofit.log.all().order_by('-start_date')])):
			log_array.append(nonprofit.log.filter(start_date=i).order_by('-start_date', '-created_on'))
		print(log_array)
		context = {
			"nonprofit": nonprofit,
			"logs_day": log_array,
		}
		return render(request, 'network/non/view_logs.html', context)
	else:
		messages.error(request, "You don't have permission to view this page!")
		return HttpResponseRedirect(nonprofit.get_absolute_url())


def report(request, network_id):
	network = get_object_or_404(Network, slug=network_id)
	return render(request, 'network/report.html', {'network': network})