from django.urls import path, re_path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9a-z-]+)/$', views.activate, name='activate'),
    path('login/', views.Login.as_view(), name='login'),

    path('profile/user/<username>', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('profile/u/<username>', views.redirect_profile, name='profile_redirect'),
    
    path('profile/user/<username>/delete', views.delete_user, name='delete_user'),
    path('profile/user/<username>/edit', views.update_user, name='update_user'),
]