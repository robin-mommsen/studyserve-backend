from django.contrib import admin
from .models import ServiceConfig

class ServiceConfigAdmin(admin.ModelAdmin):
    list_display = ['description']
    search_fields = ['description']
    ordering = ['description']

admin.site.register(ServiceConfig, ServiceConfigAdmin)
