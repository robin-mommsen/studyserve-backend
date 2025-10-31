from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import PlattformSettings, MaintenanceMessage, ScheduledCredit, Log

class PlattformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlattformSettings
        fields = ['recharge_interval', 'coin_limit', 'recharge_amount', 'last_recharge']
        read_only_fields = ['last_recharge']

class CoinAdjustmentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    reason = serializers.CharField(max_length=255)

    def validate(self, data):
        user = self.context['user']
        new_balance = user.coins + data['amount']
        if new_balance < 0:
            raise serializers.ValidationError("Balance cannot be negative.")
        return data

class MaintenanceMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceMessage
        fields = ['id', 'message', 'created_at', 'is_active']

class ScheduleCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledCredit
        fields = ['id', 'amount', 'created_at', 'date']

class LogSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model'
    )
    reference = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = ['id', 'log_type', 'description', 'content_type', 'object_id', 'reference', 'created_at', 'content_type_name']
        read_only_fields = ['id', 'log_type', 'description', 'content_type', 'object_id', 'reference', 'created_at', 'content_type_name']

    def get_reference(self, obj):
        return str(obj.reference)