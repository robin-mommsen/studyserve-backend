from django.contrib import admin
from .models import ServerConfig

class ServerConfigAdmin(admin.ModelAdmin):
    list_display = ['description', 'cpu_cores', 'ram_gb', 'disk_gb', 'cost_per_hour', 'script']
    search_fields = ['description', 'cpu_cores', 'ram_gb', 'disk_gb', 'cost_per_hour']
    ordering = ['description']

admin.site.register(ServerConfig, ServerConfigAdmin)
