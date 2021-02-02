from django.shortcuts import render, get_object_or_404
#from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .forms import *
from .models import User
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views import generic

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token


from cal.models import Calendar, Event
from network.models import Network, Nonprofit
from orgs.models import Organization

from datetime import datetime
from datetime import timedelta
from dateutil.rrule import *

from django.contrib import messages
#from django.utils.safestring import mark_safe

class SignUp(generic.CreateView):
	form_class = CustomUserCreationForm
	success_url = reverse_lazy('login')
	template_name = 'accounts/signup.html'
	

	def form_valid(self, form):
		user = form.save(commit=False)
		user.is_active = False
		user.save()
		self.object = user
		message = render_to_string('accounts/authentication_email.txt', {
			'user': user,
			'domain': settings.DOMAIN_NAME,
			'site': settings.SITE_NAME,
			'uid':urlsafe_base64_encode(force_bytes(user.pk)),
			'token':account_activation_token.make_token(user),
		})
		h_message = render_to_string('accounts/authentication_email.html', {
			'user': user,
			'domain': settings.DOMAIN_NAME,
			'site': settings.SITE_NAME,
			'uid':urlsafe_base64_encode(force_bytes(user.pk)),
			'token':account_activation_token.make_token(user),
		})
		send_mail(
			'Activate your account on ' + settings.SITE_NAME,
			message,
			settings.EMAIL_HOST_USER,
			[form.cleaned_data.get('email')],
			html_message=h_message,
		)
		messages.info(self.request, "A verification link should arrive shortly to your email address. Check your spam folder!")
		 
		return super().form_valid(form)

	def dispatch(self, *args, **kwargs):
		if self.request.user.is_authenticated:
			messages.error(self.request, "You can't sign up if you're already logged in")
			return HttpResponseRedirect(reverse('home:main'))
		else:
			return super().dispatch(*args, **kwargs)

def activate(request, uidb64, token):
	user = None
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		messages.error(request, "That activation link did not work")
		return HttpResponseRedirect(reverse_lazy('login'))

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		try:
			user_cal = Calendar.objects.get(user=user)
		except Calendar.DoesNotExist:
			user_cal = Calendar(user=user)
			user_cal.save()

			#all of this down to the return statement creates a yearly repeating account anniversary event
			today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
			pattern = rrule(freq=YEARLY, dtstart=today)

			description = "On this day in " + str(today.year) + ", your account was created!"
			aa_event = Event(rrule=pattern, all_day=True, start_time=today, end_time=today + timedelta(days=1), event_type='AA', title="Account Anniversary", description=description)
			aa_event.calendar = user_cal
			aa_event.save()

	messages.success(request, "Successfully verified your account!")
	return HttpResponseRedirect(reverse_lazy('home:main'))





class Login(LoginView):
	redirect_authenticated_user = True #overrided the class so that now logging in automatically redirects back to main
	@method_decorator(sensitive_post_parameters())
	@method_decorator(csrf_protect)
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if self.redirect_authenticated_user and self.request.user.is_authenticated:
			redirect_to = self.get_success_url()
			if redirect_to == self.request.path:
				raise ValueError(
					"Redirection loop for authenticated user detected. Check that "
					"your LOGIN_REDIRECT_URL doesn't point to a login page."
				)
			messages.error(self.request, "You are already logged in")
			return HttpResponseRedirect(redirect_to)
		return super().dispatch(request, *args, **kwargs)


def profile(request, username=None):
	context = {}
	if username:
		user = get_object_or_404(User, username=username)
		if request.user.is_authenticated and user == request.user:
			return HttpResponseRedirect(reverse('accounts:profile'))
		joined_organizations = Organization.objects.filter(Q(member=user) | Q(leader=user) | Q(moderator=user)).distinct()
		context = {
			'profile': user,
			'joined_organizations': joined_organizations,
		}
	else:
		if request.user.is_authenticated:
			user = request.user
			joined_organizations = Organization.objects.filter(Q(member=user) | Q(leader=user) | Q(moderator=user)).distinct()
			context = {
				'profile': user,
				'created_networks': Network.objects.filter(created_by=user),
				'created_nonprofits': Nonprofit.objects.filter(created_by=user),
				'joined_organizations': joined_organizations,
				'calendar' : Calendar.objects.get(user=user),
				'assigned_goals': [o.goal.all() for o in joined_organizations.exclude(Q(leader=user))] + [user.assigned_goal.all()]
			}
		else:
			messages.error(request, "You aren't logged in and can't see this page")
			return HttpResponseRedirect(reverse('home:main'))
	return render(request, 'accounts/profile.html', context)

def redirect_profile(request, username):
	return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))

@login_required
def delete_user(request, username): 
	obj = get_object_or_404(User, username=username)

	if not (request.user.username == obj.username or request.user.has_perm('accounts.delete_user')):
		messages.error(request, "You do not have permission to delete this user!")
		return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))
	else:
		if request.method =="POST": 
			obj.delete() #delete object

			#redirects:
			if request.user.has_perm('accounts.delete_user'):
				messages.success(request, "User deleted successfully")
				return HttpResponseRedirect(reverse('home:main')) #the user is an admin / moderator, don't bring them to login view
			else:
				return reverse('login')
  
	return render(request, "accounts/user_confirm_delete.html", {"object": obj})

@login_required
def update_user(request, username):
	context ={}
	obj = get_object_or_404(User, username=username)
	context["object"] = obj 

	if not (request.user.username == obj.username or request.user.has_perm('accounts.update_user')):
		messages.error(request, "You do not have permission to edit this user!")
		return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))
	else:
		form = UpdateUser(request.POST or None, instance = obj)
		if form.is_valid(): 
			form.save() 
			return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : obj.username}))
		context["form"] = form 
	return render(request, "accounts/user_update_form.html", context)