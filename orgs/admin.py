from django.contrib import admin

# Register your models here.
from .models import *
from django.forms import CheckboxSelectMultiple

class OrganizationAdmin(admin.ModelAdmin):
	list_filter = ['pub_date']
	list_display = ('title', 'pub_date', 'slug')
	search_fields = ['title']
	formfield_overrides = {
		models.ManyToManyField: {'widget': CheckboxSelectMultiple},
	}

admin.site.register(Organization, OrganizationAdmin)