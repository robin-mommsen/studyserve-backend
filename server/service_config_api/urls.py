from django.urls import path
from .views import ServiceConfigListCreateView

urlpatterns = [
    path('', ServiceConfigListCreateView.as_view(), name='service-list'),
]