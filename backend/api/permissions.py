from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with role='admin' or superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.is_superuser)
        )

class IsTeacher(permissions.BasePermission):
    """
    Allows access only to users with role='teacher' or admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and 
            request.user.role in ['teacher', 'admin']
        )

class IsStudent(permissions.BasePermission):
    """
    Allows access to students, teachers and admins.
    (If you strictly want only students, remove 'teacher' and 'admin')
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and 
            request.user.role in ['student', 'teacher', 'admin']
        )
