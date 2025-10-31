"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from management_api.views import PublicMaintenanceMessageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/servers/', include('server_api.urls')),
    path('api/services/', include('service_api.urls')),
    path('api/users/', include('user_api.urls')),
    path('api/server-configs/', include('server_config_api.urls')),
    path('api/service-configs/', include('service_config_api.urls')),
    path('api/projects/', include('project_api.urls')),
    path('api/management/', include('management_api.urls')),
    path('api/maintenance-messages/', PublicMaintenanceMessageView.as_view(), name='public-maintenance-messages'),
]
