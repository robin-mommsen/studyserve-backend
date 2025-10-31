from django.db import models
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel

class ServerConfig(TimeStampedModel):
    description = models.CharField(max_length=255)
    cpu_cores = models.IntegerField(validators=[MinValueValidator(1)])
    ram_gb = models.IntegerField(validators=[MinValueValidator(2)])
    disk_gb = models.IntegerField(validators=[MinValueValidator(5)])
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    script = models.TextField()
    is_container = models.BooleanField(default=False, blank=True)
    is_deprecated = models.BooleanField(default=False)

    class Meta:
        db_table = 'server_configs'

    def __str__(self):
        return self.description