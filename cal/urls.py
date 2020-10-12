from django.urls import path

from . import views

app_name = 'cal'
urlpatterns = [
	path('', views.index, name='index'),

	path('user/<username>/add', views.add_event, name='addevent'), #add an event to a user calendar
	path('network/<network>/add/', views.add_event, name='addevent'), #add an event to a network calendar
    path('network/<network>/<nonprofit>/add/', views.add_event, name='addevent'), #add an event to a nonprofit calendar
    path('organization/<organization>/add', views.add_event, name='add_event_org'), #add an event to an organization calendar

    path('<token>.json', views.calendar_json, name='caljson'), #add an event to an organization calendar

    path('<token>/subscribe', views.calendar_subscribe, name='subscribe'), #subscribe to a calendar
    path('<token>/unsubscribe', views.calendar_unsubscribe, name='unsubscribe'), #unsubscribe from a calendar

    path('event/', views.event_detail, name='eventdetail'), #this url ONLY exists so that I can reverse to it, then add a token in javascript

    path('event/<token>', views.event_detail, name='eventdetail'), #event detail view
    path('event/<token>/edit', views.edit_event, name='editevent'), #event edit  view
    path('event/<token>/delete', views.delete_event, name='deleteevent'), #event delete  view
    path('event/<token>/sign_up', views.event_sign_up, name='signup'), #event sign up view
	
	path('user/<username>/', views.usercal, name='usercal'), #redirect to a user detail page if that user is the logged in one
	path('u/<username>/', views.redirect_usercal, name='redirect_usercal'), #redirect to user/<username>

	path('organization/<organization>/', views.orgcal, name='orgcal'), #redirect to a user detail page if that user is the logged in one
	path('o/<organization>/', views.redirect_orgcal, name='redirect_orgcal'), #redirect to user/<username>

	path('network/<network>/', views.networkcal, name='networkcal'), #redirect to a network detail page
	path('network/<network>/<nonprofit>/', views.nonprofitcal, name='nonprofitcal'), #redirect to a nonprofit detail page
]
