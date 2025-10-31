from django.urls import path
from .views import ServerListCreateView, ServerDetailView, ServerActionView, ServerLogListView

urlpatterns = [
    path('', ServerListCreateView.as_view(), name='server-list-create'),
    path('<int:pk>/', ServerDetailView.as_view(), name='server-detail'),
    path('<int:pk>/logs/', ServerLogListView.as_view(), name='server-log-list'),
    path('<int:pk>/<str:action>/', ServerActionView.as_view(), name='server-action'),
]
