from django.db import models

import datetime, random, string
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from django.urls import reverse

from accounts.models import User

import PIL
from PIL import Image
from io import StringIO, BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from network.models import Nonprofit

# Create your models here.

class Organization(models.Model):
	title = models.CharField(max_length=75, help_text="What is the name of this organization?", unique=True, default="")
	description = models.CharField(max_length=500, help_text="A short description. This could be a mission statement, or something else.", blank=True, null=True)
	pub_date = models.DateTimeField('date published', default=timezone.now)

	#Unlike nonprofits, none of these are required
	website = models.URLField(max_length=200, help_text="If this organization has a website different from here, enter if applicable", null=True, blank=True)
	phone = models.CharField(max_length=12, help_text="Enter a phone number in the format 111-111-1111, if applicable", null=True, blank=True) #for now, I'm using a charfield but in the future I should use a phonenumber field from a library
	address = models.CharField(max_length=100, help_text="If this organization has a physical address, enter if applicable", null=True, blank=True)
	email = models.EmailField(max_length=254, help_text="Enter a relevant email to contact this organization, if applicable", null = True, blank=True)

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

	@property
	def get_participants(self):
		return self.member.all() | self.moderator.all() | self.leader.all()

	@property
	def get_leadership(self):
		return self.moderator.all() | self.leader.all()

def create_token():
		chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
		token = ''.join(random.choice(chars) for _ in range(5))
		token_list = Invitation.objects.filter(token=token, valid=True)
		while token_list:
			token = ''.join(random.choice(chars) for _ in range(5))
			token_list = Invitation.objects.filter(token=token, valid=True)
		#this while loop makes sure that if the token is found inside a list of current tokens (a duplicate token), then just keep on refreshing. Ensures uniquness
		return token
def create_token_request():
		chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
		token = ''.join(random.choice(chars) for _ in range(5))
		token_list = Request.objects.filter(token=token, approved=False)
		while token_list:
			token = ''.join(random.choice(chars) for _ in range(5))
			token_list = Request.objects.filter(token=token, approved=False)
		#this while loop makes sure that if the token is found inside a list of current tokens (a duplicate token), then just keep on refreshing. Ensures uniquness
		return token

class Invitation(models.Model):
	max_uses = models.IntegerField('Maximum Uses', help_text="What is the maximum number of times this invitation can be used? Leave blank for unlimited", null = True, blank = True, validators=[MinValueValidator(1), MaxValueValidator(100)])
	uses = models.IntegerField(default=0)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True) #invitations are paired with an organization
	expiration = models.DateTimeField(help_text='after this date, this link will no longer be valid', blank=True, null=True) #invitations can expire after a certain date
	valid = models.BooleanField(default=True) #invitations can be set to invalid, in which case they no longer work
	token = models.CharField(max_length=5) #token is the uniqueness part

	@property
	def is_not_expired(self):
		if self.expiration:
			return timezone.now() < self.expiration
		else:
			return True

	def __str__(self):
		return format(self.token)

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = create_token() #set the token on save
		return super(Invitation, self).save(*args, **kwargs)

#Users can request to join an organization
class Request(models.Model):
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	request_message = models.CharField(max_length=200, null=True, blank=True) #users can optionally add a request message
	approved = models.BooleanField(default=False)
	token = models.CharField(max_length=5) #requests have a token, too, just because using id's wouldn't be secure since you could see how many requests there are really quickly
	request_date = models.DateTimeField(default=timezone.now)

	class Meta: 
		ordering = ['-request_date']

	@property
	def is_not_approved(self):
		return not self.approved

	def __str__(self):
		return format(self.token)

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = create_token_request() #set the token on save
		return super(Request, self).save(*args, **kwargs)

class Goal(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True) #goal is applied to a specific user
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null = True, blank = True) #goal is applied to all users in an organization
	
	title = models.CharField(max_length=75, help_text="Does this goal have a specific name?", default="")
	description =  models.CharField(max_length=500, help_text="A short description of the goal", blank = True, null = True)

	hours = models.IntegerField(help_text="How many hours are wanted?", null = True, blank = True, validators=[MinValueValidator(1), MaxValueValidator(100)])
	start = models.DateTimeField('only hours after this time will count to this goal', blank=True, null=True)
	end = models.DateTimeField('only hours before this time will count to this goal', blank=True, null=True)

class TextPost(models.Model): #pretty much a comment / announcement
	title = models.CharField(max_length=128, blank=True, null=True)
	message = models.CharField(max_length=2048, default="")

	pub_date = models.DateTimeField(default=timezone.now)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True, related_name="child")
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
	allows_children = models.BooleanField(default=True, help_text="Allow replies to this announcement") #if you're a nonprofit, you might not want to have comments underneath something

	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null = True, blank = True, related_name="announcement")
	nonprofit = models.ForeignKey(Nonprofit, on_delete=models.CASCADE, null = True, blank = True, related_name="announcement")

	def __str__(self):
		if self.title:
			return format(self.title)
		else:
			return format(self.message[:5])#first five chars of message

	def get_absolute_url(self):
		if self.s_nonprofit:
			return reverse('network:announcement_detail', kwargs={'network': self.s_nonprofit.network.slug, 'slug': self.s_nonprofit.slug, 'pk': self.id})
		elif self.s_organization:
			return reverse('orgs:announcement_detail', kwargs={'organization': self.s_organization.slug, 'pk': self.id})
		else:
			return "/"

	def s_get_absolute_url(self):
		if self.s_nonprofit:
			return reverse('network:announcement_detail', kwargs={'network': self.s_nonprofit.network.slug, 'slug': self.s_nonprofit.slug, 'pk': self.s_id})
		elif self.s_organization:
			return reverse('orgs:announcement_detail', kwargs={'organization': self.s_organization.slug, 'pk': self.s_id})
		else:
			return "/"


	class Meta: 
		ordering = ['-pub_date']

	@property
	def s_id(self):
		if not self.parent:
			return self.id
		else:
			return self.parent.s_id
	@property
	def s_nonprofit(self):
		if self.nonprofit:
			return self.nonprofit
		elif self.parent:
			return self.parent.s_nonprofit
		else:
			return None

	@property
	def s_organization(self):
		if self.organization:
			return self.organization
		elif self.parent:
			return self.parent.s_organization
		else:
			return None
	
	@property
	def depth(self):
		depth = 1
		if not self.parent:
			depth = 0
		elif self.parent:
			depth += self.parent.depth
		return depth

	@property
	def get_relatives(self):
		relatives = []
		if self.parent:
			relatives.append(self)
		for i in self.child.all():
			relatives += i.get_relatives
		return relatives