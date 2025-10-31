from django.db import models
from config import settings
from core.models import TimeStampedModel
from user_api.models import User

class Project(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return self.name

class ProjectMember(TimeStampedModel):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'projects_members'
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.project.name}"

class Invitation(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(max_length=10, default='pending')

    class Meta:
        db_table = 'projects_invitations'
        unique_together = ('project', 'user')