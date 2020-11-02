from django.urls import path

from . import views

app_name = 'network'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AddNetView.as_view(), name='addnet'), #add a network
    path('<slug:slug>/delete/', views.DeleteNetView.as_view(), name='deletenet'), #delete a network
    path('<slug:slug>/update/', views.UpdateNetView.as_view(), name='updatenet'), #update a network
    path('<slug:slug>/', views.NetDetailView.as_view(), name='detail'), #shows networks in more detail

    path('<slug:network>/add/', views.AddNonView.as_view(), name='addnon'), #add a nonprofit
    path('<slug:network>/<slug:slug>/', views.NonDetailView.as_view(), name='detailnon'), #nonprofit detail view
    path('<slug:network>/<slug:slug>/update/', views.UpdateNonView.as_view(), name='updatenon'), #update a nonprofit
    path('<slug:network>/<slug:slug>/delete/', views.DeleteNonView.as_view(), name='deletenon'), #delete a nonprofit
    path('<slug:network>/<slug:slug>/represent/', views.non_represent, name='representnon'), #represent a nonprofit
    path('<slug:network>/<slug:slug>/lock/', views.non_lock, name='locknon'), #lock a nonprofit
    path('<slug:network>/<slug:slug>/unlock/', views.non_unlock, name='unlocknon'), #unlock a nonprofit

    path('<slug:network>/<slug:slug>/create_announcement/', views.create_announcement, name='create_announcement'),
    
    path('<str:network_id>/report/', views.report, name='report'),
]
