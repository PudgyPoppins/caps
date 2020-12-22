from django.urls import path

from . import views

app_name = 'logs'
urlpatterns = [
	path('', views.show_log, name='log'),
	path('user/<username>', views.show_log, name='log'),
    path('u/<username>', views.redirect_log, name='log_redirect'),
    
	path('add/', views.AddLogView.as_view(), name='add'),

	path('user/<username>/<token>', views.DetailView.as_view(), name='detail'),

	path('user/<username>/<token>/verify', views.verify, name='verify'),
	path('user/<username>/<token>/unverify', views.unverify, name='unverify'),
	path('user/<username>/<token>/deny', views.deny, name='deny'),

	path('<token>/edit', views.EditView.as_view(), name='edit'),
	path('<token>/delete', views.DeleteView.as_view(), name='delete'),
]