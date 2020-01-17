import datetime

from django import forms
from django.forms import ModelForm, CheckboxSelectMultiple
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from network.models import Network, Nonprofit

import geopy
from geopy.geocoders import Nominatim
geolocator = Nominatim()

class NetworkFormUpdate(ModelForm):
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

    class Meta:
    	model = Network
    	fields = ['title', 'src_link', 'src_file', 'lat', 'lon']
    	labels = {'lat': _('Latitude'), 'lon': _('Longitude'), 'src_link': _('Image Url'), 'src_file': _('Image File')}
    	help_texts = {'lat': _('Please enter the latitude of the location, or leave it blank to auto-generate one via the title'), 'lon': _('Please enter the longitude of the location, or leave it blank to auto-generate one via the title')} 
    def save(self, commit=True):
    	instance = super().save(commit=False)
    	try:
    		instance.lat = geolocator.geocode(self.cleaned_data.get('title'), timeout=None).latitude
    		instance.lon = geolocator.geocode(self.cleaned_data.get('title'), timeout=None).longitude
    	except geopy.exc.GeocoderTimedOut:
    		print("The geocoder could not find the coordinates based on the address. Change the address to refresh the coordinates.")
    		#TODO:Possibly flag this network as incorrect coordinates?
    	if commit:
    		instance.save()
    	return instance
class NetworkFormCreate(NetworkFormUpdate):
    def __init__(self, *args, **kwargs):
        super(NetworkFormCreate, self).__init__(*args, **kwargs)
        self.fields.pop('lat')
        self.fields.pop('lon')

class NonprofitForm(ModelForm):
    class Meta:
    	model = Nonprofit
    	exclude = ('pub_date', 'flagged', 'slug')
    	labels = {'lat': _('Latitude'), 'lon': _('Longitude'), 'src_link': _('Image Url'), 'src_file': _('Image File')}
    	help_texts = {'lat': _('Please enter the latitude of the location, or leave it blank to auto-generate one via the title'), 'lon': _('Please enter the longitude of the location, or leave it blank to auto-generate one via the title')}
    	widgets = {
            'tags': CheckboxSelectMultiple()
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
    def save(self, commit=True):
    	instance = super().save(commit=False)
    	instance.tags.set(self.cleaned_data.get('tags')) #setting the tags here since I overrided the save function
    	try:
    		instance.lat = geolocator.geocode(self.cleaned_data.get('title'), timeout=None).latitude
    		instance.lon = geolocator.geocode(self.cleaned_data.get('title'), timeout=None).longitude
    	except geopy.exc.GeocoderTimedOut:
    		print("The geocoder could not find the coordinates based on the address. Change the address to refresh the coordinates.")
    		#TODO:Possibly flag this nonprofit as incorrect coordinates?
    	if commit:
    		instance.save()
    	return instance
    def __init__(self, *args, **kwargs):
        super(NonprofitForm, self).__init__(*args, **kwargs)
        print(kwargs.get('data', None))