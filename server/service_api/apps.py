from django.apps import AppConfig

class ServiceApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service_api'


    def ready(self):
        import service_api.signals