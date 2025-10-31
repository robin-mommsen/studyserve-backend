from rest_framework import serializers
from .models import Service
from core.domain_prefix_generator import generate_unique_domain_prefix

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'created_at', 'hostname', 'expiry_timestamp', 'status', 'owner', 'project', 'service_config', 'unlimited', 'is_deleted', 'in_progress', 'domain', 'ip_address', 'vps_status']
        read_only_fields = ['status', 'unlimited', 'is_deleted', 'domain', 'hostname', 'in_progress', 'ip_address', 'vps_status']

    def create(self, validated_data):
        validated_data['status'] = 'creating'
        validated_data['hostname'] = generate_unique_domain_prefix()
        return super().create(validated_data)
