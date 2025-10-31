from django.apps import AppConfig
from django.db.models.signals import post_migrate
from .scheduler import create_schedule_task


class ManagementApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management_api'

    def ready(self):
        post_migrate.connect(create_schedule_task_on_migrate, sender=self)


def create_schedule_task_on_migrate(sender, **kwargs):
    create_schedule_task()