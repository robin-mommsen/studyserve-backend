from rest_framework import serializers
from .models import Project, ProjectMember, Invitation

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at']

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = ProjectMember
        fields = ['user_id', 'username', 'email']

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'user', 'project', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'user', 'project']