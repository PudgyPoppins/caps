from django.db import models

import datetime
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.models import User

import PIL
from PIL import Image
from io import StringIO, BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your models here.

class Organization(models.Model):
	title = models.CharField(max_length=75, help_text="What is the name of this organization?", unique=True, default="")
	description = models.CharField(max_length=500, help_text="A short description", blank=True, null=True)
	pub_date = models.DateTimeField('date published', default=timezone.now)

	src_link = models.URLField(max_length=200, help_text="Enter a url for an image representing the organization", blank=True)	
	src_file = models.ImageField(upload_to='network_images', help_text = "Submit a file for an image representing the organization", height_field=None, width_field=None, max_length=100, blank=True)
	slug = models.SlugField(max_length=100, unique=True, blank=True)

	leader = models.ManyToManyField(User, blank = True, related_name="leaders", related_query_name="leader")
	moderator = models.ManyToManyField(User, blank = True, related_name="moderators", related_query_name="moderator")
	member = models.ManyToManyField(User, blank = True, related_name="members", related_query_name="member")
	
	public = models.BooleanField(help_text="whether or not members can join without an invitation / approval", default=True)

	def __str__(self):
		return format(self.title)

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

		super(Organization, self).save(*args, **kwargs)

class Goal(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True) #goal is applied to a specific user
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null = True, blank = True) #goal is applied to all users in an organization
	
	title = models.CharField(max_length=75, help_text="Does this goal have a specific name?", default="")
	description =  models.CharField(max_length=500, help_text="A short description of the goal", blank = True, null = True)

	hours = models.IntegerField(help_text="How many hours are wanted?", null = True, blank = True, validators=[MinValueValidator(1), MaxValueValidator(100)])
	start = models.DateTimeField('only hours after this time will count to this goal', blank=True, null=True)
	end = models.DateTimeField('only hours before this time will count to this goal', blank=True, null=True)

class Textp(models.Model): #stands for text post, pretty much a comment
	title = models.CharField(max_length=75, help_text="", blank=True, null=True)
	message = models.CharField(max_length=1000, help_text="", default="")
	pub_date = models.DateTimeField('date published', default=timezone.now)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="child")
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)

	def __str__(self):
		if self.title:
			return format(self.title)
		else:
			return format(self.title[:5])#first five chars of message