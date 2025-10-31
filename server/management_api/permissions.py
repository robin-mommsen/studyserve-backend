from permissions import HasScope
from rest_framework.permissions import BasePermission

class HasManagementScope(HasScope):
    scope = 'isManagement'

class HasTeacherScope(HasScope):
    scope = 'isTeacher'

class AdminOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and HasManagementScope().has_permission(request, view)

class TeacherOrAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if HasManagementScope().has_permission(request, view):
                return True
            if HasTeacherScope().has_permission(request, view):
                return True
        return False
