from django.db import models
from django.utils.text import slugify
import datetime
from django.utils import timezone

from accounts.models import User

import PIL
from PIL import Image
from io import StringIO, BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your models here.
class Network(models.Model):
	pub_date = models.DateTimeField('date published', default=timezone.now)
	title = models.CharField(max_length=75, help_text="What town/city/location will this network be representing?", unique=True, default="")
	src_link = models.URLField(max_length=200, help_text="Enter a url for an image representing the network location", blank=True)	
	src_file = models.ImageField(upload_to='network_images', help_text = "Submit a file for an image representing the network location", height_field=None, width_field=None, max_length=100, blank=True)
	slug = models.SlugField(max_length=100, unique=True, blank=True)

	lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null = True)
	lon = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null = True)

	flagged = models.BooleanField(default=False)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)


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
		self.slug = slugify(self.title)

		#image resizing:
		if self.src_file:
			# 1024px width maximum
			basewidth = 1024
			img = Image.open(self.src_file)
			# Keep the exif data
			exif = None
			if 'exif' in img.info:
			    exif = img.info['exif']
			width_percent = (basewidth/float(img.size[0]))
			height_size = int((float(img.size[1])*float(width_percent)))
			img = img.resize((basewidth, height_size), PIL.Image.ANTIALIAS)
			img = img.convert('RGB')
			output = BytesIO()
			# save the resized file to our IO ouput with the correct format and EXIF data ;-)
			if exif:
			    img.save(output, format='JPEG', exif=exif, quality=100)
			else:
			    img.save(output, format='JPEG', quality=100)
			output.seek(0)
			self.src_file = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.src_file.name, 'image/jpeg', output.getbuffer().nbytes, None)

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
	src_file = models.ImageField(upload_to='nonprofit_images', help_text = "Submit a file for an image representing the network location", height_field=None, width_field=None, max_length=100, blank=True)

	#At least one of these forms is required to be filled out
	website = models.URLField(max_length=200, help_text="Enter the nonprofit website url, if applicable", null=True, blank=True)
	phone = models.CharField(max_length=12, help_text="Enter a phone number in the format 111-111-1111", null=True, blank=True) #for now, I'm using a charfield but in the future I should use a phonenumber field from a library
	address = models.CharField(max_length=100, help_text="Enter the nonprofit address, if applicable", null=True, blank=True)
	email = models.EmailField(max_length=254, help_text="Please enter a relevant email for volunteering, if applicable", null = True, blank=True)

	description = models.CharField(max_length=1024, help_text="What kind of work will volunteers be doing here?", null=True, blank=True)

	lat = models.DecimalField(max_digits=9, decimal_places=6, null = True, blank=True)
	lon = models.DecimalField(max_digits=9, decimal_places=6, null = True, blank=True)

	tags = models.ManyToManyField(Tag, blank=True)

	flagged = models.BooleanField(default=False)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)

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

		#image resizing:
		if self.src_file:
			# 1024px width maximum
			basewidth = 1024
			img = Image.open(self.src_file)
			# Keep the exif data
			exif = None
			if 'exif' in img.info:
			    exif = img.info['exif']
			width_percent = (basewidth/float(img.size[0]))
			height_size = int((float(img.size[1])*float(width_percent)))
			img = img.resize((basewidth, height_size), PIL.Image.ANTIALIAS)
			img = img.convert('RGB')
			output = BytesIO()
			# save the resized file to our IO ouput with the correct format and EXIF data ;-)
			if exif:
			    img.save(output, format='JPEG', exif=exif, quality=100)
			else:
			    img.save(output, format='JPEG', quality=100)
			output.seek(0)
			self.src_file = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.src_file.name, 'image/jpeg', output.getbuffer().nbytes, None)

		super(Nonprofit, self).save(*args, **kwargs)

	def __str__(self): 
		return self.title