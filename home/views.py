import pytz
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

from network.models import Network, Nonprofit
from django.utils import timezone

def main(request):
	if request.user.is_authenticated:
		if request.user.nonprofit_rep.all():
			nonprofit = request.user.nonprofit_rep.all()[0]
			return HttpResponseRedirect(reverse('network:detailnon', kwargs={'network': nonprofit.network.slug, 'slug' : nonprofit.slug}))
		else:
			network_list = Network.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
			return render(request, 'network/index.html', {"network_list": network_list})
	else:
		context = {}
		return render(request, 'home/index.html', context)

def index(request):
	context = {}
	return render(request, 'home/index.html', context)

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('home:main')
    else:
        return render(request, 'home/time.html', {'timezones': pytz.common_timezones})


def handler403(request, *args, **argv):
	response = render(request, 'home/403.html')
	response.status_code = 403
	return response

def handler404(request, *args, **argv):
	response = render(request, 'home/404.html')
	response.status_code = 404
	return response