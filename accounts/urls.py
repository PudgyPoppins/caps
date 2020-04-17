from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('profile/user/<username>', views.get_profile, name='profile'),
    path('profile/u/<username>', views.redirect_profile, name='profile_redirect'),
    path('profile/', views.current_profile, name='current_profile'),
    path('profile/user/<username>/delete', views.delete_user, name='delete_user'),
    path('profile/user/<username>/edit', views.update_user, name='update_user'),
]