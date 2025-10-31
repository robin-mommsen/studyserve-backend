from django.db import models
from config import settings
from project_api.models import Project
from core.models import TimeStampedModel
from service_config_api.models import ServiceConfig

class Service(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=63)
    service_config = models.ForeignKey(ServiceConfig, on_delete=models.SET_NULL, null=True)
    expiry_timestamp = models.IntegerField(null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, blank=True, default='creating')
    unlimited = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False)
    domain = models.CharField(max_length=64, unique=True, null=True, blank=True)
    vps_status = models.CharField(max_length=20, null=True, blank=True, default='offline')
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    in_progress = models.BooleanField(default=True)
    world_id = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'services'

    def __str__(self):
        return self.hostname
