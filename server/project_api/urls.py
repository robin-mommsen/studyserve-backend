from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, ProjectServerListView, \
    ProjectMemberListView, ProjectServiceListView, \
    ProjectInvitationListCreateView, InvitationAcceptView, InvitationDeclineView, ProjectLeaveView

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/servers/', ProjectServerListView.as_view(), name='project-server-list'),
    path('<int:pk>/services/', ProjectServiceListView.as_view(), name='project-service-list'),
    path('<int:project_id>/members/', ProjectMemberListView.as_view(), name='project-member-list'),
    path('<int:project_id>/leave/', ProjectLeaveView.as_view(), name='leave-project'),
    path('<int:project_id>/invitations/', ProjectInvitationListCreateView.as_view(), name='project-invitation-create-list'),
    path('<int:project_id>/invitations/accept/', InvitationAcceptView.as_view(), name='accept-invitation'),
    path('<int:project_id>/invitations/decline/', InvitationDeclineView.as_view(), name='decline-invitation'),
]
