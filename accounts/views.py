from django.shortcuts import render
#from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.urls import reverse_lazy
from django.views import generic

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required

#@method_decorator(user_passes_test(lambda u: not u.is_authenticated()), name='dispatch')
class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

class Profile(generic.DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'