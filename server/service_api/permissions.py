from rest_framework.permissions import BasePermission
from permissions import HasScope

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id

class HasServiceReadScope(HasScope):
    scope = 'services:read'

class HasServiceWriteScope(HasScope):
    scope = 'services:write'

class ScopedMethodPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return HasServiceReadScope().has_permission(request, view)
        elif request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return HasServiceWriteScope().has_permission(request, view)
        return False
