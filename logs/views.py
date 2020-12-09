from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_duration

from .models import Log
from accounts.models import User
from .forms import *

def show_log(request, username=None):
	context = {}
	user = None
	if username:
		user = get_object_or_404(User, username=username)
		if request.user.is_authenticated and user == request.user:
			return HttpResponseRedirect(reverse('logs:detail'))
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
	return HttpResponseRedirect(reverse('logs:detail', kwargs={'username' : username}))

class AddLogView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
	model = Log
	form_class = LogForm
	success_url = reverse_lazy('accounts:profile')
	template_name = 'logs/log_form.html'
	success_message = "Your hours have been succesfully logged"
	def form_valid(self, form):
		log = form.save(commit=False)
		log.user = self.request.user
		log.duration *= 60 #*60 because it reads as seconds, not minutes
		log.save() #saves the object, sets the id
		self.object = log
		return HttpResponseRedirect(self.get_success_url())