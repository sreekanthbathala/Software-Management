from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from .models import User, Project, Task, Training



class CanManageProject(BasePermission):
    """Allow write access if user is the project manager, OR has Manager/HR role."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ('Manager', 'HR')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.manager == request.user or request.user.role in ('Manager', 'HR')


class CanManageTask(BasePermission):
    """Allow write access if user is the task creator, OR has Manager/HR role."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ('Manager', 'HR', 'Employee')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by == request.user or request.user.role in ('Manager', 'HR')


class CanManageTraining(BasePermission):
    """Allow write access if user is the instructor, OR has Instructor/Manager/HR role."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ('Instructor', 'Manager', 'HR')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.instructor == request.user or request.user.role in ('Manager', 'HR')



