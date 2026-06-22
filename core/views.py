from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .models import User, Project, Task, Training
from .serializers import (
    ProjectSerializer, TaskSerializer, TrainingSerializer,
    CreateUserSerializer, UserSerializer, LoginSerializer,NotificationSerializer
)
from .permissions import CanManageProject, CanManageTask, CanManageTraining
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema


class IsHROrInstructor(BasePermission):
    """Only HR and Instructor roles can create new users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('HR', 'Instructor')


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer}
    )
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

    @extend_schema(
        request=None,
        responses={200: None}
    )
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class CreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsHROrInstructor]

    @extend_schema(
            request=CreateUserSerializer,
            responses={201: UserSerializer}
    )

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
    @extend_schema(responses={200: UserSerializer})
    
    def get(self, request):
        serializer= UserSerializer(request.user)
        return Response(UserSerializer(request.user).data)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, CanManageProject]
    filterset_fields = ['status', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'name']

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, CanManageTask]
    filterset_fields = ['status', 'project', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated, CanManageTraining]
    filterset_fields = ['instructor', 'date']
    search_fields = ['title', 'description']
    ordering_fields = ['date']

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]



class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None}
    )
    def list(self, request):
        user = request.user
        if user.role == 'Manager':
            projects = Project.objects.filter(manager=user)
            tasks = Task.objects.filter(project__manager=user)
            trainings = Training.objects.filter(instructor=user)
        elif user.role == 'HR':
            projects = Project.objects.all()
            tasks = Task.objects.all()
            trainings = Training.objects.all()
        elif user.role == 'Employee':
            projects = Project.objects.filter(tasks__assigned_to=user).distinct()
            tasks = Task.objects.filter(assigned_to=user)
            trainings = Training.objects.filter(attendees=user)
        elif user.role == 'Instructor':
            projects = Project.objects.filter(tasks__assigned_to__in=Training.objects.filter(instructor=user).values_list('attendees', flat=True)).distinct()
            tasks = Task.objects.filter(assigned_to__in=Training.objects.filter(instructor=user).values_list('attendees', flat=True)).distinct()
            trainings = Training.objects.filter(instructor=user)
        else:
            projects = Project.objects.none()
            tasks = Task.objects.none()
            trainings = Training.objects.none()

        data = {
            'user': {
                'username': user.username,
                'role': user.role,
            },
            'projects': ProjectSerializer(projects, many=True).data,
            'tasks': TaskSerializer(tasks, many=True).data,
            'trainings': TrainingSerializer(trainings, many=True).data,
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

def create_user_page(request):
    return render(request, 'create_user.html')

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = None

    def get_queryset(self):
        # Avoid errors when generating schema (e.g. drf-yasg swagger_fake_view)
        if getattr(self, "swagger_fake_view", False):
            from .models import Notification
            return Notification.objects.none()
        # Ensure queryset is defined lazily to avoid import/order issues
        if self.queryset is None:
            from .models import Notification
            self.queryset = Notification.objects.all()
        return self.queryset.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True,methods=['POST'])
    def mark_read(self,request,pk=None):
        notification = self.get_object()
        notification.is_read = True     
        notification.save()
        return Response({'status': 'Notification marked as read'})

from .models import Comment, ActivityLog
from .serializers import CommentSerializer, ActivityLogSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task', 'author']
    ordering_fields = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task', 'user']
    ordering_fields = ['-timestamp']

from rest_framework.parsers import MultiPartParser, FormParser
from .models import TaskAttachment
from .serializers import TaskAttachmentSerializer

class TaskAttachmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['task', 'uploaded_by']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)