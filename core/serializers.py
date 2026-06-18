from rest_framework import serializers
from .models import User, Project, Task, Training, LeaveRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'manager', 'status']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.manager:
            response['manager'] = UserSerializer(instance.manager).data
        return response

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assigned_to', 'due_date', 'status', 'created_by']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.project:
            response['project'] = ProjectSerializer(instance.project).data
        if instance.created_by:
            response['created_by'] = UserSerializer(instance.created_by).data
        if instance.assigned_to:
            response['assigned_to'] = UserSerializer(instance.assigned_to).data
        return response

class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = ['id', 'title', 'description', 'instructor', 'date', 'attendees']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.instructor:
            response['instructor'] = UserSerializer(instance.instructor).data
        response['attendees'] = UserSerializer(instance.attendees.all(), many=True).data
        return response


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'start_date', 'end_date', 'reason', 'status']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.employee:
            response['employee'] = UserSerializer(instance.employee).data
        return response

