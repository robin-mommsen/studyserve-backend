from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from core.models import TimeStampedModel
from django.contrib.contenttypes.models import ContentType

class PlattformSettings(TimeStampedModel):
    recharge_interval = models.IntegerField(default=7)
    recharge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    last_recharge = models.DateTimeField(null=True, blank=True)
    coin_limit = models.PositiveIntegerField(default=10000)

    class Meta:
        db_table = 'plattform_settings'

class MaintenanceMessage(TimeStampedModel):
    message = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'maintenance_messages'

class ScheduledCredit(TimeStampedModel):
    date = models.IntegerField(null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    class Meta:
        db_table = 'scheduled_credits'

    def __str__(self):
        return f"{self.date} - {self.amount} EUR"

class Log(TimeStampedModel):
    LOG_TYPES= [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
    ]

    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    description = models.CharField(max_length=500)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    reference = GenericForeignKey('content_type', 'object_id')
    content_type_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'logs'

    def __str__(self):
        return f"[{self.created_at}] {self.log_type}: {self.description}"

    def save(self, *args, **kwargs):
        if self.content_type:
            self.content_type_name = self.content_type.model
        super().save(*args, **kwargs)