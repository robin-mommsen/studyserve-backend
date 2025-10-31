from django.apps import AppConfig

class ProjectApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_api'

    def ready(self):
        import project_api.signals