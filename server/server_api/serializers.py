from rest_framework import serializers
from .models import Server, AnsibleScript

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['id', 'created_at', 'hostname', 'expiry_timestamp', 'ssh_keys', 'status', 'vps_status', 'owner', 'project', 'server_config', 'unlimited', 'in_progress', 'ip_address', 'world_id', 'is_deleted']
        read_only_fields = ['status', 'vps_status', 'unlimited', 'ip_address', 'world_id', 'is_deleted', 'in_progress']

    def create(self, validated_data):
        validated_data['status'] = 'creating'
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('world_id', None)
        return representation


class AnsibleScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleScript
        fields = ['id', 'description', 'script', 'parameters']
