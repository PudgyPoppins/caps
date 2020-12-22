from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from orgs.models import TextPost, Organization
from network.models import Network, Nonprofit
from .forms import *

def create_announcement_helper(request, organization=None, nonprofit=None):
	if (organization and request.user in organization.get_leadership) or (network and request.user in network.nonprofit_reps.all()) or request.user.is_staff:
		if request.method == 'POST':
			form = CreateAnnouncement(request.POST)
			if form.is_valid():
				a = form.save(commit=False)
				a.nonprofit = nonprofit
				a.organization = organization
				a.created_by = request.user
				a.save()
				messages.success(request, "Successfully added announcement")
				return HttpResponseRedirect(a.get_absolute_url())
			messages.error(request, "You have an error in your form, try again!")
		else:
			if nonprofit:
				return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network': network.slug, 'slug' : slug}))
			elif organization:
				return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))
	else:
		messages.error(request, "You don't have permission to perform this action!")
		if nonprofit:
			return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network': network.slug, 'slug' : slug}))
		elif organization:
			return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

@login_required
def create_announcement(request, network, slug):
	network = get_object_or_404(Network, slug=network)
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network=network)
	return create_announcement_helper(request, nonprofit=nonprofit)

@login_required
def create_announcement(request, organization):
	organization = get_object_or_404(Organization, slug=organization)
	return create_announcement_helper(request, organization=organization)

def announcement_detail_helper(request, a):
	context = {'a': a, 'children': a.get_relatives}
	if a.allows_children and request.user.is_authenticated:
		form = ReplyAnnouncement()
		context['form'] = form
		if request.method == 'POST':
			form = ReplyAnnouncement(request.POST)
			if form.is_valid():
				reply = form.save(commit=False)
				reply.parent = a
				reply.created_by = request.user
				reply.save()
				messages.success(request, "Successfully added reply")
	return render(request, 'lib/announcement/announcement.html', context)

def announcement_detail(request, network, slug, pk):
	network = get_object_or_404(Network, slug=network)
	nonprofit = get_object_or_404(Nonprofit, slug=slug, network=network)
	a = get_object_or_404(TextPost, nonprofit=nonprofit, id=pk, parent=None)
	return announcement_detail_helper(request, a)

def announcement_detail(request, organization, pk):
	org = get_object_or_404(Organization, slug=organization)
	a = get_object_or_404(TextPost, organization=org, id=pk, parent=None)
	return announcement_detail_helper(request, a)

class UpdateAnnouncementView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
	model = TextPost
	template_name = 'lib/announcement/announcement_update_form.html'
	success_message = "announcement was updated successfully"
	def get_form_class(self):
		if not self.object.parent:
			return CreateAnnouncement
		else:
			return ReplyAnnouncement

	def get_object(self):
		a = get_object_or_404(TextPost, id=self.kwargs['pk'])
		if self.kwargs.get('slug') and (a.s_nonprofit.slug != self.kwargs['slug'] or a.s_nonprofit.network.slug != self.kwargs['network']):
			raise Http404
		elif self.kwargs.get('organization') and (a.s_organization.slug != self.kwargs['organization']):
			raise Http404
		return a
	
	def get_success_url(self):
		print(self.object.s_get_absolute_url())
		return self.object.s_get_absolute_url()
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['a'] = self.get_object()
		return context

	def user_passes_test(self, request):
		self.object = self.get_object()
		return self.object.created_by == request.user
	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You don't have permission to perform this action!")
			return self.object.s_get_absolute_url()
		return super(UpdateAnnouncementView, self).dispatch(request, *args, **kwargs)

class DeleteAnnouncementView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
	model = TextPost
	template_name = 'lib/announcement/announcement_confirm_delete.html'
	success_message = "announcement was deleted successfully"

	def get_object(self):
		a = get_object_or_404(TextPost, id=self.kwargs['pk'])
		if self.kwargs.get('slug') and (a.s_nonprofit.slug != self.kwargs['slug'] or a.s_nonprofit.network.slug != self.kwargs['network']):
			raise Http404
		elif self.kwargs.get('organization') and (a.s_organization.slug != self.kwargs['organization']):
			raise Http404
		return a

	def get_success_url(self, **kwargs):
		if self.kwargs.get('slug'):
			return reverse('network:detailnon', kwargs={'network': self.kwargs['network'], 'slug' : self.kwargs['slug']})
		elif self.kwargs.get('organization'):
			return reverse('orgs:detail', kwargs={'slug' : self.kwargs['organization']})


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['a'] = self.get_object()
		return context

	def user_passes_test(self, request):
		self.object = self.get_object()
		if self.kwargs.get('slug'):
			network = get_object_or_404(Network, slug=self.kwargs['network'])
			nonprofit = get_object_or_404(Nonprofit, slug=self.kwargs['slug'], network=network)
			return self.object.created_by == request.user or request.user in nonprofit.nonprofit_reps.all()
		elif self.kwargs.get('organization'):
			organization = get_object_or_404(Organization, slug=self.kwargs['organization'])
			return self.object.created_by == request.user or request.user in organization.get_leadership
	
	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You don't have permission to perform this action!")
			return s_get_absolute_url()
		if self.object.parent: #if it's a reply, just delete it immediately
			self.object.delete()
			messages.success(request, "Successfully deleted reply.")
			return HttpResponseRedirect(s_get_absolute_url())
		return super(DeleteAnnouncementView, self).dispatch(request, *args, **kwargs)


def announcement_reply_helper(request, organization=None, nonprofit=None, network=None):
	if nonprofit and (a.s_nonprofit.slug != slug or a.s_nonprofit.network.slug != network):
		raise Http404
	elif organization and a.s_organization.slug != organization:
		raise Http404
	if request.method == 'POST':
		form = ReplyAnnouncement(request.POST)
		if form.is_valid():
			reply = form.save(commit=False)
			reply.parent = a
			reply.created_by = request.user
			reply.save()
			messages.success(request, "Successfully created reply.")
			return HttpResponseRedirect(reply.s_get_absolute_url())
		messages.error(request, "Please correct your form")
	return HttpResponseRedirect(a.get_absolute_url())

@login_required
def announcement_reply(request, network, slug, pk):
	a = get_object_or_404(TextPost, id=pk)
	return announcement_reply_helper(request, nonprofit=slug, network=network)

@login_required
def announcement_reply(request, organization, pk):
	a = get_object_or_404(TextPost, id=pk)
	return announcement_reply_helper(request, organization=organization)