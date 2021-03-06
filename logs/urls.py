from django.urls import path

from . import views
import lib.views

app_name = 'logs'
urlpatterns = [
	path('', views.show_log, name='log'),
	path('user/<username>', views.show_log, name='log'),
    path('u/<username>', views.redirect_log, name='log_redirect'),
    
	path('add/', views.AddLogView.as_view(), name='add'),

	path('user/<username>/<token>', views.DetailView.as_view(), name='detail'),
	path('log/<token>', views.DetailView.as_view(), name='detail'),

	path('log/<token>/verify', views.verify, name='verify'),
	path('log/<token>/unverify', views.unverify, name='unverify'),
	path('log/<token>/deny', views.deny, name='deny'),

    path('goals/create', lib.views.CreateGoal.as_view(), name='create_goal'),
    path('goals/<int:index>/update', lib.views.UpdateGoal.as_view(), name='goal_update'),
    path('goals/<int:index>/delete', lib.views.DeleteGoal.as_view(), name='goal_delete'),

	path('<token>/edit', views.EditView.as_view(), name='edit'),
	path('<token>/delete', views.DeleteView.as_view(), name='delete'),
]