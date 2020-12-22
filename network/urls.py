from django.urls import path

from . import views
import lib.views

app_name = 'network'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.search, name='search'),

    path('add/', views.AddNetView.as_view(), name='addnet'), #add a network
    path('<slug:slug>/delete/', views.DeleteNetView.as_view(), name='deletenet'), #delete a network
    path('<slug:slug>/update/', views.UpdateNetView.as_view(), name='updatenet'), #update a network
    path('<slug:slug>/', views.NetDetailView.as_view(), name='detail'), #shows networks in more detail

    path('nonprofit/add/', views.AddNonView.as_view(), name='addnon'), #add a nonprofit w/o specifying the network (it's a search button, now)
    path('<slug:network>/add/', views.AddNonView.as_view(), name='addnon'), #add a nonprofit
    path('<slug:network>/<slug:slug>/', views.NonDetailView.as_view(), name='detailnon'), #nonprofit detail view
    path('<slug:network>/<slug:slug>/update/', views.UpdateNonView.as_view(), name='updatenon'), #update a nonprofit
    path('<slug:network>/<slug:slug>/delete/', views.DeleteNonView.as_view(), name='deletenon'), #delete a nonprofit
    path('<slug:network>/<slug:slug>/represent/', views.non_represent, name='representnon'), #represent a nonprofit
    path('<slug:network>/<slug:slug>/lock/', views.non_lock, name='locknon'), #lock a nonprofit
    path('<slug:network>/<slug:slug>/unlock/', views.non_unlock, name='unlocknon'), #unlock a nonprofit
    
    path('<slug:network>/<slug:slug>/logs/', views.view_logs, name='view_logs'), #view and approve submitted nonprofit hour logs

    path('<slug:network>/<slug:slug>/announcements/create', lib.views.create_announcement, name='create_announcement'),
    path('<slug:network>/<slug:slug>/announcements/<int:pk>/', lib.views.announcement_detail, name='announcement_detail'),
    path('<slug:network>/<slug:slug>/announcements/<int:pk>/update', lib.views.UpdateAnnouncementView.as_view(), name='announcement_update'),
    path('<slug:network>/<slug:slug>/announcements/<int:pk>/delete', lib.views.DeleteAnnouncementView.as_view(), name='announcement_delete'),
    path('<slug:network>/<slug:slug>/announcements/<int:pk>/reply', lib.views.announcement_reply, name='announcement_reply'),
    
    path('<str:network_id>/report/', views.report, name='report'),
]
