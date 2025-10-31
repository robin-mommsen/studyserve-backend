from rest_framework.permissions import BasePermission

class HasScope(BasePermission):
    def __init__(self, scope=None):
        if scope:
            self.scope = scope

    def has_permission(self, request, view):
        try:
            token_scopes = request.auth.get("scope", "")
            scopes = token_scopes.split()
        except (AttributeError, KeyError):
            scopes = []

        return request.auth and self.scope in scopes

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)