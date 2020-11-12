from django.urls import path

from . import views
import lib.views

app_name = 'orgs'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('add/', views.AddOrgView.as_view(), name='addorg'), #add an organization
    path('<slug:slug>/delete/', views.DeleteOrgView.as_view(), name='deleteorg'), #delete an organization
    path('<slug:slug>/update/', views.UpdateOrgView.as_view(), name='updateorg'), #update an organization
    path('<slug:slug>/', views.OrgDetailView.as_view(), name='detail'), #shows organizations in more detail

    path('<slug:organization>/kick/<username>', views.kick_user, name='kick'), #kick user
    path('<slug:organization>/invite/<username>', views.invite_user, name='invite'), #add user
    path('<slug:organization>/promote/<username>', views.promote_user, name='promote'), #promote user
    path('<slug:organization>/demote/<username>', views.demote_user, name='demote'), #demote user

    path('<slug:organization>/generate_invite/', views.CreateInvitation.as_view(), name='geninvite'), #generate an invitation
    path('token/<token>/delete/', views.delete_invitation, name='delinvite'), #generate an invitation
    path('join/<token>', views.join, name='join'), #join an organization
    path('<slug:organization>/request_access/', views.CreateRequest.as_view(), name='reqorg'), #request to join an organization
    path('<slug:organization>/<token>/approve/', views.approve_request, name='appreq'), #approve request
    path('<slug:organization>/<token>/deny/', views.deny_request, name='delreq'), #deny request
    path('<slug:organization>/leave/', views.leave, name='leave'), #leave an organization
    path('<slug:organization>/transfer_leadership', views.transfer_leadership, name='transfer'), #leave an organization

    path('<slug:organization>/announcements/create', lib.views.create_announcement, name='create_announcement'),
    path('<slug:organization>/announcements/<int:pk>/', lib.views.announcement_detail, name='announcement_detail'),
    path('<slug:organization>/announcements/<int:pk>/update', lib.views.UpdateAnnouncementView.as_view(), name='announcement_update'),
    path('<slug:organization>/announcements/<int:pk>/delete', lib.views.DeleteAnnouncementView.as_view(), name='announcement_delete'),
    path('<slug:organization>/announcements/<int:pk>/reply', lib.views.announcement_reply, name='announcement_reply'),

    #path('<slug:network>/add/', views.AddNonView.as_view(), name='addnon'), #add a nonprofit
    #path('<slug:network>/<slug:slug>/', views.NonDetailView.as_view(), name='detailnon'), #nonprofit detail view
    #path('<slug:network>/<slug:slug>/update/', views.UpdateNonView.as_view(), name='updatenon'), #update a nonprofit
    #path('<slug:network>/<slug:slug>/delete/', views.DeleteNonView.as_view(), name='deletenon'), #delete a nonprofit
    
    #path('<str:network_id>/report/', views.report, name='report'),
]
