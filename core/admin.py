from django.contrib import admin
from .models import User, Project, Task, Training, LeaveRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'status', 'start_date', 'end_date')
    list_filter = ('status',)
    search_fields = ('name', 'description')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'due_date')
    list_filter = ('status', 'project')
    search_fields = ('title', 'description')

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'date')
    list_filter = ('instructor',)
    search_fields = ('title', 'description')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'status')
    list_filter = ('status',)
    search_fields = ('employee__username', 'reason')