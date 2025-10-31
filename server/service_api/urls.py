from django.urls import path
from .views import ServiceListCreateView, ServiceDetailView, ServiceLogListView, ServiceActionView

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='service-list-create'),
    path('<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('<int:pk>/logs/', ServiceLogListView.as_view(), name='service-log-list'),
    path('<int:pk>/<str:action>/', ServiceActionView.as_view(), name='service-action'),
]
