from django.contrib import admin
from .models import Service

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'service_config_id', 'expiry_timestamp', 'status', 'owner_id', 'created_at', 'project_id']
    search_fields = ['hostname', 'service_config_id', 'status', 'owner_id', 'project_id']
    ordering = ['hostname']

admin.site.register(Service, ServiceAdmin)
