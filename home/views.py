from django.shortcuts import render
from django.views.generic.base import TemplateView
# Create your views here.
from django.http import HttpResponse

from network.models import Network, Nonprofit
from django.utils import timezone

def main(request):
	print(request.user)
	if request.user.is_authenticated:
		network_list = Network.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
		return render(request, 'network/index.html', {"network_list": network_list})
	else:
		context = {}
		return render(request, 'home/index.html', context)

def index(request):
	context = {}
	return render(request, 'home/index.html', context)

def handler403(request, *args, **argv):
	response = render(request, 'home/403.html')
	response.status_code = 403
	return response

def handler404(request, *args, **argv):
	response = render(request, 'home/404.html')
	response.status_code = 404
	return response