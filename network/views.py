from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView

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

class AddNetView(CreateView):
    model = Network
    #fields = ['title', 'src_link', 'src_file']
    form_class = NetworkForm
    success_url = reverse_lazy('network:index')
class DeleteNetView(DeleteView):
	model = Network
	success_url = reverse_lazy('network:index')
class UpdateNetView(UpdateView):
	slug_url_kwarg = 'slug'
	model = Network
	form_class = NetworkForm
	template_name_suffix = '_update_form'
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.slug})


class NetDetailView(generic.DetailView):
    model = Network
    slug_url_kwarg: 'slug'
    template_name = 'network/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reasons'] = ["General trolling", "The network name is not accurate / inappropiate", "The network image is not accurate / inappropiate", "The coordinates are wrong"]
        return context

class AddNonView(CreateView):
    model = Nonprofit
    form_class = NonprofitFormCreate
    def get_success_url(self):
    	return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
    def form_valid(self, form):
    	nonprofit = form.save(commit=False)
    	nonprofit.network = get_object_or_404(Network, slug=self.kwargs['network'])
    	tag_temp_var = form.cleaned_data.get('tags') #this gets the tag data
    	nonprofit.save() #saves the object, sets the id

    	nonprofit.tags.set(tag_temp_var) #saves the previous tag data after the id is created
    	nonprofit.save()
    	self.object = nonprofit
    	return HttpResponseRedirect(self.get_success_url())
class UpdateNonView(UpdateView):
	model = Nonprofit
	form_class = NonprofitFormUpdate
	template_name_suffix = '_update_form'
	success_url = reverse_lazy('network:index')
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})
class DeleteNonView(DeleteView):
	model = Nonprofit
	success_url = reverse_lazy('network:index')
	def get_queryset(self):
		return Nonprofit.objects.filter(network__slug=self.kwargs['network'])
	def get_success_url(self):
		return reverse('network:detail', kwargs={'slug' : self.object.network.slug})

class NonDetailView(generic.DetailView):
    model = Nonprofit
    template_name = 'network/non.html'
    def get_queryset(self):
        return Nonprofit.objects.filter(network__slug=self.kwargs['network'])


def report(request, network_id):
	network = get_object_or_404(Network, slug=network_id)
	return render(request, 'network/report.html', {'network': network})