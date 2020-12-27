from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_duration

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Log
from accounts.models import User
from .forms import *

def show_log(request, username=None):
	context = {}
	user = None
	if username:
		user = get_object_or_404(User, username=username)
		if request.user.is_authenticated and user == request.user:
			return HttpResponseRedirect(reverse('logs:log'))
	else:
		if request.user.is_authenticated:
			user = request.user
		else:
			messages.error(request, "You aren't logged in and can't see this page")
			return HttpResponseRedirect(reverse('home:main'))
	context['user'] = user
	context['logs'] = user.log.all()
	return render(request, 'logs/log.html', context)

def redirect_log(request, username):
	return HttpResponseRedirect(reverse('logs:log', kwargs={'username' : username}))

class AddLogView(LoginRequiredMixin, generic.CreateView):
	model = Log
	form_class = LogForm
	success_url = reverse_lazy('logs:log') #reverse_lazy('accounts:profile')
	template_name = 'logs/log_form.html'
	def form_valid(self, form):
		log = form.save(commit=False)
		log.user = self.request.user
		log.duration *= 60 #*60 because it reads as seconds, not minutes
		log.save() #saves the object, sets the id
		self.object = log
		messages.success(self.request, "Your time has been successfully logged")
		return HttpResponseRedirect(self.get_success_url())

def find(self=None, token=None, username=None):
	token = token
	username = username
	if self:
		token = self.kwargs.get('token')
		username = self.kwargs.get('username')
	if token:
		queryset = Log.objects.filter(**{'token': token})
		if username:
			queryset = queryset.filter(**{'user__username': username})
		try:
			# Get the single item from the filtered queryset
			obj = queryset.get()
			return obj
		except queryset.model.DoesNotExist:
			raise Http404(_("No %(verbose_name)s found matching the query") % {'verbose_name': queryset.model._meta.verbose_name})
	else:
		raise Http404(_("No token specified. xkcd 2200"))

class DetailView(generic.DetailView):
	model = Log
	def get_object(self, queryset=None):
		return find(self=self)

@login_required
def verify(request, username, token):
	log = find(username=username, token=token)
	if request.user in log.nonprofit.nonprofit_reps.all() or request.user.is_staff:
		log.processed = True
		if not log.verified:
			if log.user:
				send_mail(
						"Volunteering log at %s verified" % log.nonprofit.title,
						render_to_string('logs/snippets/verify_email.txt', {'log': log, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
						settings.EMAIL_HOST_USER,
						[log.user.email],
						html_message=render_to_string('logs/snippets/verify_email.html', {'log': log, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
					)
			log.verified = request.user
			messages.success(request, 'Successfully verified log')
		else:
			messages.info(request, 'This log is already verified by %s' % log.verified)
		log.save()
		return HttpResponseRedirect(reverse('network:view_logs', kwargs={'network' : log.nonprofit.network.slug, 'slug': log.nonprofit.slug}))
	else:
		messages.error(request, "You don't have permission to perform this action!")
		return HttpResponseRedirect(log.nonprofit.get_absolute_url())
@login_required
def unverify(request, username, token):
	log = find(username=username, token=token)
	if request.user in log.nonprofit.nonprofit_reps.all() or request.user.is_staff:
		log.processed = False
		if log.verified:
			log.verified = None
			messages.success(request, 'Successfully unverified log')
		else:
			messages.info(request, 'This log is already unverified')
		log.save()
		return HttpResponseRedirect(reverse('network:view_logs', kwargs={'network' : log.nonprofit.network.slug, 'slug': log.nonprofit.slug}))
	else:
		messages.error(request, "You don't have permission to perform this action!")
		return HttpResponseRedirect(log.nonprofit.get_absolute_url())

@login_required
def deny(request, username, token):
	log = find(username=username, token=token)
	if request.user in log.nonprofit.nonprofit_reps.all() or request.user.is_staff:
		if request.method == 'POST':
			form = DenyForm(request.POST)
			if form.is_valid():
				if log.user:
					send_mail(
							"Volunteering log at %s denied" % log.nonprofit.title,
							render_to_string('logs/snippets/deny_email.txt', {'log': log, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME, 'reason': form.cleaned_data['reason']}),
							settings.EMAIL_HOST_USER,
							[log.user.email],
							html_message=render_to_string('logs/snippets/deny_email.html', {'log': log, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME, 'reason': form.cleaned_data['reason']}),
						)
				log.processed = True
				log.save()
				messages.success(request, 'Successfully denied volunteering log')
		return HttpResponseRedirect(reverse('network:view_logs', kwargs={'network' : log.nonprofit.network.slug, 'slug': log.nonprofit.slug}))
	else:
		messages.error(request, "You don't have permission to perform this action!")
		return HttpResponseRedirect(log.nonprofit.get_absolute_url())


class EditView(LoginRequiredMixin, generic.UpdateView):
	model = Log
	form_class = LogForm

	def get_object(self, queryset=None):
		return find(self=self)
	def get_success_url(self):
		return reverse('logs:detail', kwargs={'username' : self.object.user.username, 'token': self.object.token})

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (self.object.user == request.user)
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to edit this log!")
			return HttpResponseRedirect(reverse('logs:detail', kwargs={'token' : self.object.token}))
		return super(EditView, self).dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		prev_duration = self.get_object().duration
		log = form.save(commit=False)
		log.duration *= 60 #*60 because it reads as seconds, not minutes
		if log.verified and (len(form.changed_data) > 1 or form.changed_data == ['duration'] and form.cleaned_data['duration'] * 60 != prev_duration):
			log.verified = False #unverify it if the data changes
			log.processed = False
		log.save() #saves the object, sets the id
		self.object = log
		messages.success(self.request, "Successfully updated log")
		return HttpResponseRedirect(self.get_success_url())

class DeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
	model = Log
	success_url = reverse_lazy('logs:log')
	success_message = "Successfully deleted log"

	def get_object(self, queryset=None):
		return find(self=self)

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (self.object.user == request.user)
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to delete this log!")
			return HttpResponseRedirect(reverse('logs:detail', kwargs={'token' : self.object.token}))
		return super(DeleteView, self).dispatch(request, *args, **kwargs)
