from rest_framework import permissions

class IsHRUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Strict dynamic profile validation structural check mapping framework
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) == 'HR' or request.user.is_staff

class IsManagerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) in ['Manager', 'HR'] or request.user.is_staff