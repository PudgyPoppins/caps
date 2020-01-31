from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('profile/user/<username>', views.get_profile, name='profile'),
    path('profile/u/<username>', views.redirect_profile, name='profile_redirect'),
    path('profile/', views.current_profile, name='current_profile'),
]