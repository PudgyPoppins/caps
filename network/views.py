from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView


from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.
from .models import Network, Nonprofit
from network.forms import NetworkForm, NonprofitFormCreate, NonprofitFormUpdate

class IndexView(generic.ListView):
	template_name = 'network/index.html'
	context_object_name = 'network_list'

	def get_queryset(self):
		"""Return networks filtered by most recent (and not in the future)"""
		return Network.objects.filter(
			pub_date__lte=timezone.now()
		).order_by('-pub_date')#[:5] uncomment this to show only most recent 5

class AddNetView(LoginRequiredMixin, CreateView):
	model = Network
	#fields = ['title', 'src_link', 'src_file']
	form_class = NetworkForm
	success_url = reverse_lazy('network:index')
	template_name = 'network/net/network_form.html'
	def form_valid(self, form):
		form.instance.created_by = self.request.user #sets the created_by user to the current one
		return super().form_valid(form)

class DeleteNetView(LoginRequiredMixin, DeleteView):
	model = Network
	success_url = reverse_lazy('network:index')
	template_name = 'network/net/network_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return (self.object.created_by == request.user or request.user.has_perm('network.delete_network')) #return whether or not the current user created this object, or if they have explicit permission to delete networks
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			messages.error(request, "You do not have permission to delete this network")
			return HttpResponseRedirect(reverse('network:detail', kwargs={'slug' : self.object.slug}))
		return super(DeleteNetView, self).dispatch(request, *args, **kwargs)

class UpdateNetView(LoginRequiredMixin, UpdateView):
	slug_url_kwarg = 'slug'
	model = Network
	form_class = NetworkForm
	template_name = 'network/net/network_update_form.html'
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.slug})


class NetDetailView(generic.DetailView):
	model = Network
	slug_url_kwarg: 'slug'
	template_name = 'network/net/network_detail.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['is_on_detail_page'] = True
		context['reasons'] = ["General trolling", "The network name is not accurate / inappropiate", "The network image is not accurate / inappropiate", "The coordinates are wrong"]
		return context


class AddNonView(LoginRequiredMixin, CreateView):
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


def report(request, network_id):
	network = get_object_or_404(Network, slug=network_id)
	return render(request, 'network/report.html', {'network': network})