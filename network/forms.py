import datetime

from django import forms
from django.forms import ModelForm, CheckboxSelectMultiple
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from network.models import Network, Nonprofit

import geopy
from geopy.geocoders import MapBox
geolocator = MapBox(api_key='pk.eyJ1IjoicHVkZ3lwb3BwaW5zIiwiYSI6ImNqdnBiaDAwMDI3dzIzenFyZjc4Z2s1MGgifQ.ZY1iUikoHZ5fZqqcvYidpw')

class NetworkForm(ModelForm):
    def clean_pub_date(self):
        data = self.cleaned_data['pub_date']
        # Check if a date is not in the future more than one day. 
        if data.date() > datetime.date.today() + datetime.timedelta(days=1):
            raise ValidationError(_('Invalid date - published date cannot be in the future'))
        # Remember to always return the cleaned data.
        return data
    def clean_lat(self):
    	lat = self.cleaned_data['lat']
    	if lat is not None:
	    	if lat > 180 or lat < -180:
	    		raise ValidationError(_('Invalid latitude - latitude must be between -180 and 180'))
    	return lat
    def clean_lon(self):
    	lon = self.cleaned_data['lon']
    	if lon is not None:
	    	if lon > 180 or lon < -180:
	    		raise ValidationError(_('Invalid longitude - longitude must be between -180 and 180'))
    	return lon
    def clean_image(self):
        image = self.cleaned_data.get('src_file', False)
        if image:
            if image._size > MAX_UPLOAD_SIZE:
                raise ValidationError("Image file too large ( > 2.5MB )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    class Meta:
    	model = Network
    	fields = ['title', 'src_link', 'src_file', 'lat', 'lon']
    	labels = {'lat': _('Latitude'), 'lon': _('Longitude'), 'src_link': _('Image Url'), 'src_file': _('Image File')}
    	help_texts = {'lat': _('Please enter the latitude of the location, or leave it blank to auto-generate one via the title'), 'lon': _('Please enter the longitude of the location, or leave it blank to auto-generate one via the title')} 
    	widgets = {'lat': forms.HiddenInput(), 'lon': forms.HiddenInput(),}

class NonprofitFormUpdate(ModelForm):
    class Meta:
    	model = Nonprofit
    	exclude = ('pub_date', 'flagged', 'slug')
    	labels = {'lat': _('Latitude'), 'lon': _('Longitude'), 'src_link': _('Image Url'), 'src_file': _('Image File')}
    	help_texts = {'lat': _('Please enter the latitude of the location, or leave it blank to auto-generate one via the address'), 'lon': _('Please enter the longitude of the location, or leave it blank to auto-generate one via the address')}
    	widgets = {
            'tags': CheckboxSelectMultiple(),
            'lat': forms.HiddenInput(), 'lon': forms.HiddenInput(),
        }
    def clean_pub_date(self):
        data = self.cleaned_data['pub_date']
        if data.date() > datetime.date.today() + datetime.timedelta(days=1):
            raise ValidationError(_('Invalid date - published date cannot be in the future'))
        return data
    def clean_lat(self):
    	lat = self.cleaned_data['lat']
    	if lat is not None:
	    	if lat > 180 or lat < -180:
	    		raise ValidationError(_('Invalid latitude - latitude must be between -180 and 180'))
    	return lat
    def clean_lon(self):
    	lon = self.cleaned_data['lon']
    	if lon is not None:
	    	if lon > 180 or lon < -180:
	    		raise ValidationError(_('Invalid longitude - longitude must be between -180 and 180'))
    	return lon
    def clean(self):
    	file = self.cleaned_data.get('src_file', False)
    	url = self.cleaned_data.get('src_link', False)
    	if url and file:
    		raise ValidationError("You cannot upload both an image url and an image file. Please upload one or the other.")
    	if self.cleaned_data['website'] is None and self.cleaned_data['phone'] is None and self.cleaned_data['address'] is None and self.cleaned_data['email'] is None:
    		print('aww man')
    		raise ValidationError("At least one of these forms (website, phone, address, email) needs to be filled out")

    '''def save(self, commit=True):
    	instance = super().save(commit=False)
    	#instance.tags.set(self.cleaned_data.get('tags')) #setting the tags here since I overrided the save function
    	#I moved the above line to the views.py createview
    	try:
    		if self.cleaned_data.get('address') is not None and (self.cleaned_data.get('lat') is None or self.cleaned_data.get('lon') is None):
	    		print(self.cleaned_data.get('address'))
	    		location = geolocator.geocode(self.cleaned_data.get('address'), timeout=None)
	    		if location is not None:
		    		instance.lat = location.latitude
		    		instance.lon = location.longitude
		    	else:
		    		print("The geocoder could not find the coordinates based on this information. You should change the address or something.")
		    		#set coords to None for now.
		    		instance.lat = None
		    		instance.lon = None
    		elif self.cleaned_data.get('address') is None:
    			#no address, no coords
    			instance.lat = None
    			instance.lon = None
    	except geopy.exc.GeocoderTimedOut:
    		print("The geocoder timed out.")
    	if commit:
    		instance.save()
    	return instance
    def __init__(self, *args, **kwargs):
        super(NonprofitFormUpdate, self).__init__(*args, **kwargs)'''

class NonprofitFormCreate(NonprofitFormUpdate):
    def __init__(self, *args, **kwargs):
        super(NonprofitFormCreate, self).__init__(*args, **kwargs)
        self.fields.pop('network')