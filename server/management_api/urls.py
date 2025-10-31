from django.urls import path
from .views import ServerListView, ServerDetailView, UserListView, UserDetailView, ServerConfigListView, \
    ServerConfigDetailView, ServiceListView, ServiceDetailView, ServiceConfigListView, ServiceConfigDetailView, \
    ProjectListView, ProjectDetailView, PlattformSettingsView, UserBalanceUpdateView, \
    ServerLimitationUpdateView, MaintenanceMessageListView, MaintenanceMessageDetailView \
    , ServerActionView, ScheduleCreditListView, ScheduleCreditDetailView, LogListView, LogDetailView, \
    InvitationListView, InvitationDetailView, ServiceActionView

urlpatterns = [
    path('servers/', ServerListView.as_view(), name='server-list'),
    path('servers/<int:pk>/', ServerDetailView.as_view(), name='server-detail'),
    path('servers/<int:pk>/<str:action>/', ServerActionView.as_view(), name='server-action'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:pk>/<str:action>/', ServiceActionView.as_view(), name='service-action'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('server-configs/', ServerConfigListView.as_view(), name='server-config-list'),
    path('server-configs/<int:pk>/', ServerConfigDetailView.as_view(), name='server-config-detail'),
    path('service-configs/', ServiceConfigListView.as_view(), name='service-config-list'),
    path('service-configs/<int:pk>/', ServiceConfigDetailView.as_view(), name='service-config-detail'),
    path('logs/', LogListView.as_view(), name='log-list'),
    path('logs/<int:pk>/', LogDetailView.as_view(), name='log-detail'),
    path('maintenance-messages/', MaintenanceMessageListView.as_view(), name='maintenance-message-list'),
    path('maintenance-messages/<int:pk>/', MaintenanceMessageDetailView.as_view(), name='maintenance-message-detail'),
    path('plattform-settings/', PlattformSettingsView.as_view(), name='plattform-settings'),
    path('users/balance/', UserBalanceUpdateView.as_view(), name='user-coin-update'),
    path('servers/limitation/', ServerLimitationUpdateView.as_view(), name='set-server-limitation'),
    path('schedule-tasks/', ScheduleCreditListView.as_view(), name='scheduled-task-list'),
    path('schedule-tasks/<int:pk>/', ScheduleCreditDetailView.as_view(), name='scheduled-task-detail'),
    path('invitations/', InvitationListView.as_view(), name='invitation-list'),
    path('invitations/<int:pk>/', InvitationDetailView.as_view(), name='invitation-detail'),
]