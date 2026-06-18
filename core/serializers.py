from rest_framework import serializers
from .models import User, Project, Task, Training, LeaveRequest, Notification, Comment, ActivityLog, TaskAttachment
from django.utils import timezone


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
        read_only_fields = ['manager']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.manager:
            response['manager'] = UserSerializer(instance.manager).data
        return response

    def validate(self, data):
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date."})
        return data

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assigned_to', 'priority', 'due_date', 'status', 'created_by']
        read_only_fields = ['created_by']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.project:
            response['project'] = ProjectSerializer(instance.project).data
        if instance.created_by:
            response['created_by'] = UserSerializer(instance.created_by).data
        if instance.assigned_to:
            response['assigned_to'] = UserSerializer(instance.assigned_to).data
        return response

    def validate(self, data):
        project = data.get('project', getattr(self.instance, 'project', None))
        due_date = data.get('due_date', getattr(self.instance, 'due_date', None))
        
        if project and due_date:
            if due_date < project.start_date or due_date > project.end_date:
                raise serializers.ValidationError({
                    "due_date": f"Task due date must be within the project's timeline ({project.start_date} to {project.end_date})."
                })
        return data

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

    def validate_date(self, value):
        if not self.instance and value < timezone.now().date():
            raise serializers.ValidationError("Training date cannot be in the past.")
        return value


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'start_date', 'end_date', 'reason', 'status']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.employee:
            response['employee'] = UserSerializer(instance.employee).data
        return response

    def validate(self, data):
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date."})
        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.user:
            response['user'] = UserSerializer(instance.user).data
        return response

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.author:
            response['author'] = UserSerializer(instance.author).data
        return response

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'task', 'user', 'action', 'timestamp']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.user:
            response['user'] = UserSerializer(instance.user).data
        return response

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['id', 'task', 'uploaded_by', 'file', 'uploaded_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.uploaded_by:
            response['uploaded_by'] = UserSerializer(instance.uploaded_by).data
        return response
