from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .models import User, Project, Task, Training, LeaveRequest
from .serializers import (
    ProjectSerializer, TaskSerializer, TrainingSerializer,
    LeaveRequestSerializer, CreateUserSerializer, UserSerializer, LoginSerializer,
)
from .permissions import CanManageProject, CanManageTask, CanManageTraining, CanManageLeaveRequest
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.permissions import BasePermission


class IsHROrInstructor(BasePermission):
    """Only HR and Instructor roles can create new users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('HR', 'Instructor')


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
            })
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class CreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsHROrInstructor]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': f'User "{user.username}" created successfully',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )



class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, CanManageProject]
    filterset_fields = ['status', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'name']

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, CanManageTask]
    filterset_fields = ['status', 'project', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'status']

class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated, CanManageTraining]
    filterset_fields = ['instructor', 'date']
    search_fields = ['title', 'description']
    ordering_fields = ['date']

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, CanManageLeaveRequest]
    filterset_fields = ['status', 'employee']
    search_fields = ['reason']
    ordering_fields = ['start_date', 'end_date']

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        if user.role == 'Manager':
            projects = Project.objects.filter(manager=user)
            tasks = Task.objects.filter(project__manager=user)
            trainings = Training.objects.filter(instructor=user)
            leave_requests = LeaveRequest.objects.filter(employee__in=Task.objects.filter(project__manager=user).values_list('assigned_to', flat=True))
        elif user.role == 'HR':
            projects = Project.objects.all()
            tasks = Task.objects.all()
            trainings = Training.objects.all()
            leave_requests = LeaveRequest.objects.all()
        elif user.role == 'Employee':
            projects = Project.objects.filter(tasks__assigned_to=user).distinct()
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
            'user': {
                'username': user.username,
                'role': user.role,
            },
            'projects': ProjectSerializer(projects, many=True).data,
            'tasks': TaskSerializer(tasks, many=True).data,
            'trainings': TrainingSerializer(trainings, many=True).data,
            'leave_requests': LeaveRequestSerializer(leave_requests, many=True).data,
        }
        return Response(data)

def home_view(request):
    return render(request, 'home.html')

def login_page(request):
    return render(request, 'login.html')

def dashboard_page(request):
    return render(request, 'dashboard.html')

def projects_page(request):
    return render(request, 'projects.html')

def tasks_page(request):
    return render(request, 'tasks.html')

def trainings_page(request):
    return render(request, 'trainings.html')

def leave_requests_page(request):
    return render(request, 'leave_requests.html')

def create_user_page(request):
    return render(request, 'create_user.html')