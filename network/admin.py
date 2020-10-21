from django.contrib import admin
from django.utils.safestring import mark_safe

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# Register your models here.
#from .models import Network, Nonprofit, Tag
from .models import *
from django.forms import CheckboxSelectMultiple

class NonprofitInline(admin.TabularInline):
	model = Nonprofit
	extra = 1

class NetworkAdmin(admin.ModelAdmin):
	inlines = [NonprofitInline]
	list_filter = ['flagged', 'pub_date']
	list_display = ('title', 'pub_date', 'was_flagged', 'slug')
	search_fields = ['title']

class NonprofitAdmin(admin.ModelAdmin):
	list_display = ('title', 'network', 'pub_date', 'was_flagged')
	list_filter = ['flagged', 'pub_date']
	search_fields = ['title']
	formfield_overrides = {
		models.ManyToManyField: {'widget': CheckboxSelectMultiple},
	}

def approve_applicant(modeladmin, request, queryset):
	queryset.update(approved=True)
	for i in queryset:
		i.save()
		if i not in i.nonprofit.nonprofit_reps.all(): #if they get approved, add them into the nonprofit_rep for their desired nonprofit thing
			i.nonprofit.nonprofit_reps.add(i.user)
			i.nonprofit.save()

			email = i.user.email
			if i.email:
				email = i.email
			send_mail(
				"You've been approved as a nonprofit representative for " + i.nonprofit.title,
				render_to_string('network/snippets/rep_email.txt', {'r': i, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
				'pudgypoppins@gmail.com',
				[email],
				html_message=render_to_string('network/snippets/rep_email.html', {'r': i, 'domain':settings.DOMAIN_NAME, 'site': settings.SITE_NAME}),
			)
approve_applicant.short_description = 'Approve applicant for nonprofit'

class RepApplicantAdmin(admin.ModelAdmin):
	list_display = ('user', 'nonprofit', 'approved')
	list_filter = ['approved', 'nonprofit']
	search_fields = ['user', 'nonprofit', 'approved']
	actions = [approve_applicant]
	def image_display(self, obj):
		x = "<div>"
		x += "<img src='/media/applicant_images/%s' height='500px'/>" %(obj.src_file)
		x += "</div>"
		return mark_safe(x)

	def get_readonly_fields(self, request, obj=None):
		fields = [f.name for f in RepApplicant._meta.get_fields()] + ["image_display"]
		fields.remove("id")
		fields.remove("approved")
		return fields


admin.site.register(Network, NetworkAdmin)
admin.site.register(Nonprofit, NonprofitAdmin)
admin.site.register(Tag)
admin.site.register(RepApplicant, RepApplicantAdmin)