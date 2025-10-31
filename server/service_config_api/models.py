from django.db import models
from core.models import TimeStampedModel
from server_config_api.models import ServerConfig

class ServiceConfig(TimeStampedModel):
    description = models.CharField(max_length=255)
    server_config = models.ForeignKey(ServerConfig, on_delete=models.DO_NOTHING, null=False)
    ansible_script = models.TextField()
    is_deprecated = models.BooleanField(default=False)

    class Meta:
        db_table = 'service_configs'

    def __str__(self):
        return self.description