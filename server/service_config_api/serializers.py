from rest_framework import serializers
from management_api.permissions import HasManagementScope
from .models import ServiceConfig

class ServiceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceConfig
        fields = '__all__'

    def get_script(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and HasManagementScope().has_permission(request, None):
            return obj.ansible_script
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not (user and HasManagementScope().has_permission(request, None)):
            rep.pop('ansible_script', None)
        return rep