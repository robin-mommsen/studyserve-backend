from django.urls import path
from .views import ServerConfigListCreateView

urlpatterns = [
    path('', ServerConfigListCreateView.as_view(), name='server-list'),
]