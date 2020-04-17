from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView


from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe

# Create your views here.
from cal.models import Calendar
from accounts.models import User

from .models import Organization, Goal, TextPost, Invitation
from .forms import * #honestly, I'm gonna use all of them, just import 'em all

class IndexView(generic.ListView):
	template_name = 'orgs/index.html'
	context_object_name = 'org_list'

	def get_queryset(self):
		"""Return organizations filtered by most recent (and not in the future)"""
		return Organization.objects.filter(
			pub_date__lte=timezone.now()
		).order_by('-pub_date')#[:5] uncomment this to show only most recent 5

class AddOrgView(LoginRequiredMixin, CreateView):
	model = Organization
	#fields = ['title', 'src_link', 'src_file']
	form_class = OrganizationForm
	template_name = 'orgs/orgs/organization_form.html'
	
	def get_success_url(self):
		return reverse('orgs:detail', kwargs={'slug' : self.object.slug})
	def form_valid(self, form):
		organization = form.save(commit=False)
		organization.save() #saves the object, sets the id

		organization.leader.add(self.request.user) #sets the leader user to the current one

		self.object = organization

		organization_cal = Calendar(organization=self.object) #create a new calendar for the organization
		organization_cal.save()
		return HttpResponseRedirect(self.get_success_url())

class DeleteOrgView(LoginRequiredMixin, DeleteView):
	model = Organization
	success_url = reverse_lazy('orgs:index')
	template_name = 'orgs/orgs/organization_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (request.user in self.object.leader.all() or request.user.has_perm('network.delete_organization')) #return whether or not the current user is a leader, or if they have explicit permission to delete networks
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to delete this organization!")
			return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : self.object.slug}))
		return super(DeleteOrgView, self).dispatch(request, *args, **kwargs)

class UpdateOrgView(LoginRequiredMixin, UpdateView):
	slug_url_kwarg = 'slug'
	model = Organization
	form_class = OrganizationForm
	template_name = 'orgs/orgs/organization_update_form.html'
	def get_success_url(self):
		return reverse('orgs:detail', kwargs={'slug' : self.object.slug})

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (request.user in self.object.leader.all() or request.user in self.object.moderator.all() or request.user.has_perm('network.update_organization')) #return whether or not the current user is a leader, or if they have explicit permission to delete networks
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to update this organization!")
			return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : self.object.slug}))
		return super(UpdateOrgView, self).dispatch(request, *args, **kwargs)

class OrgDetailView(generic.DetailView):
	model = Organization
	slug_url_kwarg: 'slug'
	template_name = 'orgs/orgs/organization_detail.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['calendar'] = Calendar.objects.get(organization=self.object.id)
		if self.request.user.is_authenticated:
			user_requests = Request.objects.filter(user=self.request.user, approved=False, organization=self.object.id)
			if len(user_requests) > 0:
				context['has_made_request'] = True
			else:
				context['has_made_request'] = False
		else:
			context['has_made_request'] = False
		return context

class CreateInvitation(LoginRequiredMixin, CreateView):
	model = Invitation
	form_class = InvitationForm
	template_name = 'orgs/inv/invitation_form.html'
	def get_success_url(self):
		return reverse('orgs:detail', kwargs={'slug' : self.object.organization.slug})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['organization'] = get_object_or_404(Organization, slug=self.kwargs['organization'])#pass the organization data to the createview so it can use it for auto form stuff
		return context
	def form_valid(self, form):
		invitation = form.save(commit=False)
		invitation.organization = get_object_or_404(Organization, slug=self.kwargs['organization'])
		invitation.save() #saves the object, sets the id
		self.object = invitation

		return HttpResponseRedirect(self.get_success_url())

@login_required
def join(request, token):
	token = Invitation.objects.filter(token=token, valid=True)
	if token:
		token = token[0] # Replace queryset with model instance
		if token.max_uses:#token invalid case 1: too many uses
			if token.uses >= token.max_uses:
				token.valid = False
				token.save()
				messages.error(request, "This invitation link is no longer valid!")
				return HttpResponseRedirect(reverse('orgs:index'))
		if token.expiration: #token invalid case 2: it's expired
			if timezone.now() > token.expiration:
				token.valid = False
				token.save()
				messages.error(request, "This invitation link is no longer valid!")
				return HttpResponseRedirect(reverse('orgs:index'))
		#Otherwise, it's valid, continue as planned
		organization = Organization.objects.get(id=token.organization.id)
		#If they're already a part of the organization
		if request.user in organization.member.all() or request.user in organization.moderator.all() or request.user in organization.leader.all():
			messages.info(request, "You're already a part of this organization!")
			return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : token.organization.slug}))
		organization.member.add(request.user) #add the user as a member now! Yay, they joined!
		token.uses += 1
		token.save()
		if token.uses >= token.max_uses:
				token.valid = False
				token.save()
		messages.success(request, "You've successfully joined this organization!")
		return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : token.organization.slug}))
	else:
		messages.error(request, "That invitation link doesn't exist!")
		return HttpResponseRedirect(reverse('orgs:index'))

class CreateRequest(LoginRequiredMixin, CreateView):
	model = Request
	form_class = RequestForm
	template_name = 'orgs/req/request_form.html'
	success_message = "You've successfully requested to join %(organization)s"
	def get_success_message(self, cleaned_data):
		organization = get_object_or_404(Organization, slug=self.kwargs['organization'])
		return self.success_message % dict(
			cleaned_data,
			organization=organization,
		)

	def dispatch(self, request, *args, **kwargs):
		organization = get_object_or_404(Organization, slug=self.kwargs['organization'])
		user_requests = Request.objects.filter(user=request.user, approved=False, organization=organization)
		if len(user_requests) > 0:
			messages.error(request, "You've already made a request to join this organization!")
			return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))
		if request.user in organization.member.all() or request.user in organization.leader.all() or request.user in organization.moderator.all():
			messages.error(request, "You're already in this organization!")
			return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))
		return super(CreateRequest, self).dispatch(request, *args, **kwargs)

	def get_success_url(self):
		return reverse('orgs:detail', kwargs={'slug' : self.object.organization.slug})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['organization'] = get_object_or_404(Organization, slug=self.kwargs['organization'])#pass the organization data to the createview so it can use it for auto form stuff
		return context
	def form_valid(self, form):
		request = form.save(commit=False)
		request.organization = get_object_or_404(Organization, slug=self.kwargs['organization'])
		request.user = self.request.user
		if not request.request_message or len(request.request_message) < 3:
			request.request_message = "I'd like to join this organization, please!"
		request.save() #saves the object, sets the id
		self.object = request
		return HttpResponseRedirect(self.get_success_url())

@login_required
def approve_request(request, organization, token):
	req = Request.objects.filter(token=token, approved=False)
	organization = get_object_or_404(Organization, slug=organization)
	if request.user in organization.leader.all() or request.user in organization.moderator.all():
		if req:
			req = req[0]
			req.approved = True
			req.save()
			organization.member.add(req.user) #add the user as a member now! Yay, they joined!
			messages.success(request, "%s was added to %s successfully" %(request.user.username, organization.title))
		else:
			messages.error(request, "This request doesn't exist!")
	else:
		messages.error(request, "You don't have permission to approve this request!")
	return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

@login_required
def deny_request(request, organization, token):
	req = Request.objects.filter(token=token, approved=False)
	organization = get_object_or_404(Organization, slug=organization)
	if request.user in organization.leader.all() or request.user in organization.moderator.all():
		if req:
			req = req[0]
			req.delete()
			messages.success(request, "You've successfully denied %s's request to join %s" %(req.user, organization.title))
		else:
			messages.error(request, "This request doesn't exist!")
	else:
		messages.error(request, "You don't have permission to deny this request!")
	return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

@login_required
def kick_user(request, organization, username):
	organization = get_object_or_404(Organization, slug=organization)
	user = get_object_or_404(User, username=username)

	undo_link = reverse('orgs:add', kwargs={'organization': organization.slug, 'username': user.username})

	if request.user in organization.leader.all(): #leaders can only kick moderators if they're demoted first
		if user in organization.member.all():
			organization.member.remove(user) #removing member
			messages.success(request, mark_safe("You've successfully kicked %s from %s. <a href='%s'>Undo?</a>" %(user, organization.title, undo_link)))
		elif user in organization.moderator.all():
			demote_link = reverse('orgs:demote', kwargs={'organization': organization.slug, 'username': user.username})
			messages.error(request, mark_safe("You have to <a href='%s'>demote this user</a> first!" %(demote_link))) #demote ask
		elif user in organization.leader.all():
			messages.error(request, "Leaders can't be deleted")
		else:
			messages.error(request, "Couldn't find a user with the username %s in this organization" %(user))
	elif request.user in organization.moderator.all(): #moderators can only kick basic members
		if user in organization.member.all():
			organization.member.remove(user) #removing member
			messages.success(request, mark_safe("You've successfully kicked %s from %s. <a href='%s'>Undo?</a>" %(user, organization.title, undo_link)))
		elif user in organization.moderator.all():
			messages.error(request, "You don't have permission to kick other helpers!")
		elif user in organization.leader.all():
			messages.error(request, "You don't have permission to kick a leader!")
		else:
			messages.error(request, "Couldn't find a user with the username %s in this organization" %(user))
	else:
		messages.error(request, "You don't have permission to perform this action!")
	return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

@login_required
def add_user(request, organization, username):
	organization = get_object_or_404(Organization, slug=organization)
	user = get_object_or_404(User, username=username)
	if request.user in organization.leader.all() or request.user in organization.moderator.all():
		organization.member.add(user)
		undo_link = reverse('orgs:kick', kwargs={'organization': organization.slug, 'username': user.username})
		messages.success(request, mark_safe("You've successfully added %s to %s. <a href='%s'>Undo?</a>" %(user, organization.title, undo_link)))
	else:
		messages.error(request, "You don't have permission to perform this action!")
	return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

@login_required
def promote_user(request, organization, username):
	organization = get_object_or_404(Organization, slug=organization)
	user = get_object_or_404(User, username=username)
	if request.user in organization.leader.all(): #only leaders can promote
		if user in organization.member.all():
			organization.member.remove(user)
			organization.moderator.add(user)
			undo_link = reverse('orgs:demote', kwargs={'organization': organization.slug, 'username': user.username})
			messages.success(request, mark_safe("You've successfully promoted %s to moderator. <a href='%s'>Undo?</a>" %(user, undo_link)))
		elif user in organization.moderator.all() or user in organization.leader.all():
			messages.error(request, "This user can't be promoted!")
		else:
			messages.error(request, "Couldn't find a user with the username %s in this organization" %(user))
	else:
		messages.error(request, "You don't have permission to perform this action!")
	return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

@login_required
def demote_user(request, organization, username):
	organization = get_object_or_404(Organization, slug=organization)
	user = get_object_or_404(User, username=username)
	if request.user in organization.leader.all(): #only leaders can demote
		if user in organization.moderator.all():
			organization.moderator.remove(user)
			organization.member.add(user)
			undo_link = reverse('orgs:promote', kwargs={'organization': organization.slug, 'username': user.username})
			messages.success(request, mark_safe("You've successfully demoted %s from moderator. <a href='%s'>Undo?</a>" %(user, undo_link)))
		elif user in organization.member.all() or user in organization.leader.all():
			messages.error(request, "This user can't be demoted!")
		else:
			messages.error(request, "Couldn't find a user with the username %s in this organization" %(user))
	else:
		messages.error(request, "You don't have permission to perform this action!")
	return HttpResponseRedirect(reverse('orgs:detail', kwargs={'slug' : organization.slug}))

'''class AddNonView(LoginRequiredMixin, CreateView):
	model = Nonprofit
	form_class = NonprofitFormCreate
	template_name = 'network/non/nonprofit_form.html'
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['network'] = get_object_or_404(Network, slug=self.kwargs['network'])#pass the network data to the createview so it can use it for coords and stuff
		return context
	def form_valid(self, form):
		form.instance.created_by = self.request.user
		nonprofit = form.save(commit=False)
		nonprofit.network = get_object_or_404(Network, slug=self.kwargs['network'])
		tag_temp_var = form.cleaned_data.get('tags') #this gets the tag data
		nonprofit.save() #saves the object, sets the id

		nonprofit.tags.set(tag_temp_var) #saves the previous tag data after the id is created
		nonprofit.save()
		self.object = nonprofit

		network_calendar = Calendar.objects.get(network=self.object.network.id)
		nonprofit_cal = Calendar(nonprofit=self.object, network_calendar=network_calendar)
		nonprofit_cal.save() #these last three lines create a calendar for this nonprofit

		return HttpResponseRedirect(self.get_success_url())

class UpdateNonView(LoginRequiredMixin, UpdateView):
	model = Nonprofit
	form_class = NonprofitFormUpdate
	success_url = reverse_lazy('network:index')
	template_name = 'network/non/nonprofit_update_form.html'
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['network'] = get_object_or_404(Network, slug=self.kwargs['network'])#pass the network data to the updateview so it can use it for coords and stuff
		return context

class DeleteNonView(LoginRequiredMixin, DeleteView):
	model = Nonprofit
	success_url = reverse_lazy('network:index')
	template_name = 'network/non/nonprofit_confirm_delete.html'
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
	
	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (self.object.created_by == request.user or request.user.has_perm('network.delete_nonprofit'))
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to delete this nonprofit")
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
		return context


def report(request, network_id):
	network = get_object_or_404(Network, slug=network_id)
	return render(request, 'network/report.html', {'network': network})'''