from django.urls import path
from django.conf.urls import include

from . import views

app_name = 'cal'
urlpatterns = [
    path('', views.index, name='index'),
]
