from django.shortcuts import render
#from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .models import User
from django.urls import reverse_lazy
from django.views import generic

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required

#@method_decorator(user_passes_test(lambda u: not u.is_authenticated()), name='dispatch')
class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

def get_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'accounts/profile.html', {"profile":user}) #I'm passing this info through as profile instead of user because if the profile is not the user's own, I want them to be able to see their stuff still