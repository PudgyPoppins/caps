from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from orgs.models import TextPost, Organization, Goal
from orgs.forms import GoalForm
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
	success_message = "Announcement was updated successfully"
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
	success_message = "Announcement was deleted successfully"

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

def get_goal(self): #this method has support of manually specifying a <username> in the url, but I don't user that later on
	organization = self.kwargs.get('organization')
	username = self.kwargs.get('username')
	if not username:
		username = self.request.user.username
	index = self.kwargs.get('index')

	#if not(organization ^ username) or not index:
	#proceed if the XOR of organization and username is true (it's one or the other, not both or neither), AND an index is specified
	if index is None:
		raise Http404(_("Invalid url. xkcd 2200"))
	
	queryset = Goal.objects.filter(**{'organization__slug': organization}).order_by('created_on')
	if not organization:
		queryset = queryset.filter(**{'user__username':username})
	
	try:
		obj = queryset[index]
		return obj
	except queryset.model.DoesNotExist:
		raise Http404(_("No %(verbose_name)s found matching the query") % {'verbose_name': queryset.model._meta.verbose_name})
	except IndexError:
		raise Http404

class CreateGoal(LoginRequiredMixin, CreateView):
	model = Goal
	form_class = GoalForm
	template_name = 'lib/goal/goal_form.html'

	def get_object(self, queryset=None):
		return get_goal(self)
	def get_success_url(self):
		if self.kwargs.get('organization'):
			return reverse('orgs:detail', kwargs={'slug' : self.kwargs.get('organization')})
		elif self.kwargs.get('username'):
			return reverse('accounts:profile', kwargs={'username' : self.kwargs.get('username')})
		else:
			return reverse_lazy('accounts:profile')

	def get_organization(self):
		if self.kwargs.get('organization'):
			return Organization.objects.get(slug=self.kwargs.get('organization'))
		else:
			return None

	def user_passes_test(self, request):
		if self.kwargs.get('organization'):
			organization = self.get_organization()
			return(request.user in organization.get_leadership)
		return True

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You don't have permission to create this goal!")
			return HttpResponseRedirect(reverse(self.get_success_url()))
		return super(CreateGoal, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['organization'] = self.get_organization()
		return context

	def form_valid(self, form):
		goal = form.save(commit=False)
		goal.created_by = self.request.user
		if self.kwargs.get('organization'):
			goal.organization = self.get_organization()
		elif self.kwargs.get('username'):
			user = get_object_or_404(User, username=self.kwargs.get('username'))
			goal.user = user
		else:
			goal.user = self.request.user

		if goal.organization:
			if goal.end >= timezone.now().date():
				send_mail(
						"Volunteering goal for %s created" % goal.organization,
						render_to_string('lib/emails/notify_goal.txt', {'goal': goal, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
						settings.EMAIL_HOST_USER,
						[u.email for u in goal.organization.member.all() | goal.organization.moderator.all()],
						html_message=render_to_string('lib/emails/notify_goal.html', {'goal': goal, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
					)
		goal.save()
		self.object = goal
		messages.success(self.request, "Successfully added goal")
		return HttpResponseRedirect(self.get_success_url())

class UpdateGoal(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
	model = Goal
	form_class = GoalForm
	template_name = 'lib/goal/goal_form.html'
	success_message = "Goal was updated successfully"

	def get_object(self, queryset=None):
		return get_goal(self)
	def get_success_url(self):
		if self.kwargs.get('organization'):
			return reverse('orgs:detail', kwargs={'slug' : self.kwargs.get('organization')})
		elif self.kwargs.get('username'):
			return reverse('accounts:profile', kwargs={'username' : self.kwargs.get('username')})
		else:
			return reverse_lazy('accounts:profile')

	def user_passes_test(self, request):
		if self.kwargs.get('organization'):
			organization = get_object_or_404(Organization, slug=self.kwargs.get('organization'))
			return(request.user in organization.get_leadership)
		return True

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You don't have permission to update this goal!")
			return HttpResponseRedirect(reverse(self.get_success_url()))
		return super(UpdateGoal, self).dispatch(request, *args, **kwargs)

class DeleteGoal(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
	model = Goal
	form_class = GoalForm
	template_name = 'lib/goal/goal_confirm_delete.html'
	success_message = "Goal was deleted successfully"

	def get_object(self, queryset=None):
		return get_goal(self)
	def get_success_url(self):
		if self.kwargs.get('organization'):
			return reverse('orgs:detail', kwargs={'slug' : self.kwargs.get('organization')})
		elif self.kwargs.get('username'):
			return reverse('accounts:profile', kwargs={'username' : self.kwargs.get('username')})
		else:
			return reverse_lazy('accounts:profile')

	def user_passes_test(self, request):
		if self.kwargs.get('organization'):
			organization = get_object_or_404(Organization, slug=self.kwargs.get('organization'))
			return(request.user in organization.get_leadership)
		return True

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You don't have permission to delete this goal!")
			return HttpResponseRedirect(reverse(self.get_success_url()))
		return super(DeleteGoal, self).dispatch(request, *args, **kwargs)