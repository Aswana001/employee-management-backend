from rest_framework import serializers
from .models import Notification, AuditLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['recipient', 'created_at', 'read_at']


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.ReadOnlyField(source='actor.email')

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = [
            'actor', 'action', 'module_name', 
            'description', 'ip_address', 'user_agent', 'timestamp'
        ]