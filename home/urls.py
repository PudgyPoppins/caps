from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.index, name='index'),
    path('time/', views.set_timezone, name='set_timezone'),
    
    #path('issues')
]
