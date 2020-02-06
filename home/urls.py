from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.index, name='index'),
    
    #path('issues')
]
