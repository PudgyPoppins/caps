from django.urls import path

from . import views

app_name = 'logs'
urlpatterns = [
	path('', views.show_log, name='detail'),
	path('user/<username>', views.show_log, name='detail'),
    path('u/<username>', views.redirect_log, name='detail_redirect'),
    
	path('add/', views.AddLogView.as_view(), name='add'),
]