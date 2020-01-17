from django.contrib import admin

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

admin.site.register(Network, NetworkAdmin)
admin.site.register(Nonprofit, NonprofitAdmin)
admin.site.register(Tag)
