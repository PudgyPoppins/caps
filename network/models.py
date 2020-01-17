from django.db import models
from django.utils.text import slugify
import datetime
from django.utils import timezone

from geopy.geocoders import Nominatim
geolocator = Nominatim()

# Create your models here.
class Network(models.Model):
    pub_date = models.DateTimeField('date published', default=timezone.now)
    title = models.CharField(max_length=75, help_text="What town/city/location will this network be representing?", unique=True, default="")
    src_link = models.URLField(max_length=200, help_text="Enter a url for an image representing the network location", blank=True)	
    src_file = models.ImageField(upload_to=None, help_text = "Submit a file for an image representing the network location", height_field=None, width_field=None, max_length=100, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null = True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null = True)

    flagged = models.BooleanField(default=False)

    def __str__(self): 
    	return self.title

    def was_published_recently(self):
    	now = timezone.now()
    	return now - datetime.timedelta(days=7) <= self.pub_date <= now #returns true if it was created within the last week
    def was_flagged(self):
    	return self.flagged
    was_flagged.admin_order_field = 'flagged'
    was_flagged.boolean = True
    was_flagged.short_description = 'Flagged / Reported?'

    def save(self, *args, **kwargs):
    	self.netslug = slugify(self.title)
    	super(Network, self).save(*args, **kwargs)

class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(max_length=50, unique=True)
	
	class Meta: 
		ordering = ['name']

	def __str__(self):
		return format(self.name)

class Nonprofit(models.Model):
	network = models.ForeignKey(Network, on_delete=models.CASCADE) #Each nonprofit belongs to one network
	pub_date = models.DateTimeField('date published', default=timezone.now)
	title = models.CharField(max_length=75, help_text="Enter the network name")
	src_link = models.URLField(max_length=200, help_text="Enter a url for an image representing the network location", blank=True)	
	src_file = models.ImageField(upload_to=None, help_text = "Submit a file for an image representing the network location", height_field=None, width_field=None, max_length=100, blank=True)

	#TODO: require at least one of these forms to be filled out
	website = models.URLField(max_length=200, help_text="Enter the nonprofit website url, if applicable", null=True, blank=True)
	phone = models.CharField(max_length=12, help_text="Enter a phone number in the format 111-111-1111", null=True, blank=True) #for now, I'm using a charfield but in the future I should use a phonenumber field from a library
	address = models.CharField(max_length=100, help_text="Enter the nonprofit address, if applicable", null=True, blank=True)
	email = models.EmailField(max_length=254, help_text="Please enter a relevant email for volunteering, if applicable", null = True, blank=True)

	lat = models.DecimalField(max_digits=9, decimal_places=6, null = True, blank=True)
	lon = models.DecimalField(max_digits=9, decimal_places=6, null = True, blank=True)

	tags = models.ManyToManyField(Tag, blank=True)
	flagged = models.BooleanField(default=False)

	slug = models.SlugField(max_length=100, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields= ['network','title'], name='unique_np_naming'),
		]

	def was_flagged(self):
		return self.flagged
	was_flagged.admin_order_field = 'flagged'
	was_flagged.boolean = True
	was_flagged.short_description = 'Flagged / Reported?'

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Nonprofit, self).save(*args, **kwargs)

	def __str__(self): 
		return self.title