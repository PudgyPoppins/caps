"""caps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.conf.urls.static import static

from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog

from django.conf import settings
from django.views.generic import RedirectView

import network.views

urlpatterns = [
    path('', include('home.urls')),

    path('network/', include('network.urls')),
    #path('networks/', RedirectView.as_view(url='/network/')), #redirect

    path('calendar/', include('cal.urls')),

    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'home.views.handler403'
handler404 = 'home.views.handler404'

if settings.DEBUG: # hopefully helps with images
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

js_info_dict = {
    'packages': ('recurrence', ),
}

# jsi18n can be anything you like here
urlpatterns += [
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), js_info_dict),
]