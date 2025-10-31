from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Server
from management_api.models import Log

@receiver(pre_save, sender=Server)
def track_server_changes(sender, instance, **kwargs):
    if instance.pk:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_instance = old_instance

@receiver(post_save, sender=Server)
def log_server_save(sender, instance, created, **kwargs):
    if created:
        description = f"Server created with Hostname: {instance.hostname}"
        log_type = 'INFO'
    else:
        changes = []
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                if old_value != new_value:
                    changes.append(f"{field_name} changed from {old_value} to {new_value}")

        if not changes:
            return

        description = "; ".join(changes)
        log_type = 'INFO'

    Log.objects.create(
        log_type=log_type,
        description=description,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id
    )

@receiver(post_save, sender=Server)
def log_server_deletion(sender, instance, **kwargs):
    if instance.is_deleted:
        description = f"Server marked as deleted: Hostname: {instance.hostname}"
        log_type = 'INFO'

        Log.objects.create(
            log_type=log_type,
            description=description,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )