from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Project, Task, Training, LeaveRequest
from .serializers import ProjectSerializer, TaskSerializer, TrainingSerializer, LeaveRequestSerializer
from .permissions import IsAdmin, IsLeaveRequestEmployeeOrReadOnly, IsManager, IsHR, IsEmployee, IsInstructor, IsProjectManagerOrReadOnly, IsTaskCreatorOrReadOnly, IsTrainingInstructorOrReadOnly
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectManagerOrReadOnly, IsManager, IsHR, IsAdmin]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskCreatorOrReadOnly, IsManager, IsHR, IsAdmin]

class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated, IsTrainingInstructorOrReadOnly, IsInstructor, IsManager, IsHR, IsAdmin]

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, IsLeaveRequestEmployeeOrReadOnly, IsManager, IsHR, IsAdmin, IsEmployee]

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        if user.role == 'Manager':
            projects = Project.objects.filter(manager=user)
            tasks = Task.objects.filter(project__manager=user)
            trainings = Training.objects.filter(instructor=user)
            leave_requests = LeaveRequest.objects.filter(employee__in=Project.objects.filter(manager=user).values_list('manager', flat=True))
        elif user.role == 'HR':
            projects = Project.objects.all()
            tasks = Task.objects.all()
            trainings = Training.objects.all()
            leave_requests = LeaveRequest.objects.all()
        elif user.role == 'Employee':
            projects = Project.objects.filter(task__assigned_to=user).distinct()
            tasks = Task.objects.filter(assigned_to=user)
            trainings = Training.objects.filter(attendees=user)
            leave_requests = LeaveRequest.objects.filter(employee=user)
        elif user.role == 'Instructor':
            projects = Project.objects.filter(tasks__assigned_to__in=Training.objects.filter(instructor=user).values_list('attendees', flat=True)).distinct()
            tasks = Task.objects.filter(assigned_to__in=Training.objects.filter(instructor=user).values_list('attendees', flat=True)).distinct()
            trainings = Training.objects.filter(instructor=user)
            leave_requests = LeaveRequest.objects.filter(employee__in=Training.objects.filter(instructor=user).values_list('attendees', flat=True))
        else:
            projects = Project.objects.none()
            tasks = Task.objects.none()
            trainings = Training.objects.none()
            leave_requests = LeaveRequest.objects.none()

        data = {
            'projects': ProjectSerializer(projects, many=True).data,
            'tasks': TaskSerializer(tasks, many=True).data,
            'trainings': TrainingSerializer(trainings, many=True).data,
            'leave_requests': LeaveRequestSerializer(leave_requests, many=True).data,
        }
        return Response(data)

