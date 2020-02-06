from django.urls import path
from django.conf.urls import include, re_path

from . import views

app_name = 'cal'
urlpatterns = [
	path('', views.index, name='index'),
	
	path('user/<username>/', views.usercal, name='usercal'), #redirect to a user detail page if that user is the logged in one
	path('u/<username>/', views.redirect_usercal, name='redirect_usercal'), #redirect to user/<username>

	path('<network>/', views.networkcal, name='networkcal'), #redirect to a network detail page
	path('<network>/<nonprofit>/', views.nonprofitcal, name='nonprofitcal'), #redirect to a nonprofit detail page

	path('<slug:network>/add/', views.AddEventView.as_view(), name='addevent'), #add an event to a network
    path('<slug:network>/<slug:slug>/add/', views.AddEventView.as_view(), name='addevent'), #add an event to a nonprofit
]
