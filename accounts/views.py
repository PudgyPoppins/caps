from django.shortcuts import render, get_object_or_404
#from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .models import User
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views import generic

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required

from network.models import Network, Nonprofit

#@method_decorator(user_passes_test(lambda u: not u.is_authenticated()), name='dispatch')
class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

def get_profile(request, username):
    user = get_object_or_404(User, username=username)
    created_networks = Network.objects.filter(created_by=user)
    created_nonprofits = Nonprofit.objects.filter(created_by=user)
    context = {
    	'profile': user,
        'created_networks': created_networks,
        'created_nonprofits': created_nonprofits,
    }
    return render(request, 'accounts/profile.html', context) #I'm passing this info through as profile instead of user because if the profile is not the user's own, I want them to be able to see their stuff still

def redirect_profile(request, username):
	return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))