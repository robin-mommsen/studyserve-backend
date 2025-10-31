from rest_framework.permissions import BasePermission, SAFE_METHODS
from permissions import HasScope
from project_api.models import ProjectMember

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return obj.owner == user or ProjectMember.objects.filter(project=obj, user=user).exists()

        return obj.owner == user

class HasProjectReadScope(HasScope):
    scope = 'projects:read'

class HasProjectWriteScope(HasScope):
    scope = 'projects:write'

class ScopedMethodPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return HasProjectReadScope().has_permission(request, view)
        elif request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return HasProjectWriteScope().has_permission(request, view)
        return False
