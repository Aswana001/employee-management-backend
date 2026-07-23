from rest_framework import permissions

class IsHRUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (getattr(request.user, 'role', None) == 'HR' or request.user.is_staff))

class IsManagerOrHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (getattr(request.user, 'role', None) in ['Manager', 'HR'] or request.user.is_staff))