from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import User
from management_api.models import Log

@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    if created:
        description = f"User created with Username: {instance.username}"
        log_type = 'INFO'
    else:
        dirty_fields = instance.get_dirty_fields()
        dirty_fields.pop('coins', None)

        changes = [
            f"{field} changed from {old_value} to {getattr(instance, field)}"
            for field, old_value in dirty_fields.items()
        ]
        description = "; ".join(changes) if changes else "No significant changes"
        log_type = 'INFO'

    if created or dirty_fields:
        Log.objects.create(
            log_type=log_type,
            description=description,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )