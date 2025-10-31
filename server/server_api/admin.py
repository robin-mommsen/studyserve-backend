from django.contrib import admin
from .models import Server

class ServerAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'server_config_id', 'expiry_timestamp', 'ssh_keys', 'status', 'owner_id', 'created_at', 'project_id']
    search_fields = ['hostname', 'server_config_id', 'status', 'owner_id', 'project_id']
    ordering = ['hostname']

admin.site.register(Server, ServerAdmin)
