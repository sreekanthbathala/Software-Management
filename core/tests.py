from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Project, Task, Training, LeaveRequest, Notification, Comment, ActivityLog
import datetime

User = get_user_model()

class CoreAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users with different roles
        self.hr_user = User.objects.create_user(username='hr_user', password='password', role='HR')
        self.manager_user = User.objects.create_user(username='manager_user', password='password', role='Manager')
        self.employee_user = User.objects.create_user(username='employee_user', password='password', role='Employee')
        
        # Authenticate as HR for setup
        self.client.force_authenticate(user=self.hr_user)
        
        # Create a basic project
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Desc",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30),
            manager=self.manager_user
        )

    def test_project_validation(self):
        """Test that end_date cannot be before start_date"""
        url = reverse('project-list')
        data = {
            "name": "Invalid Project",
            "description": "Desc",
            "start_date": "2026-12-31",
            "end_date": "2026-01-01",
            "manager": self.manager_user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_date', response.data)

    def test_task_creation_and_signals(self):
        """Test creating a task generates a Notification and ActivityLog"""
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(ActivityLog.objects.count(), 0)

        task = Task.objects.create(
            title="Setup DB",
            description="DB setup",
            project=self.project,
            created_by=self.manager_user,
            assigned_to=self.employee_user,
            due_date=datetime.date.today() + datetime.timedelta(days=5),
            priority="High"
        )

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(ActivityLog.objects.count(), 1)
        
        notif = Notification.objects.first()
        self.assertEqual(notif.user, self.employee_user)
        
        # Test status change logs activity
        task.status = 'In Progress'
        task.save()
        
        self.assertEqual(ActivityLog.objects.count(), 2)

    def test_permissions(self):
        """Test role-based access control"""
        # Employee tries to create a project
        self.client.force_authenticate(user=self.employee_user)
        url = reverse('project-list')
        data = {
            "name": "Employee Project",
            "description": "Desc",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "manager": self.manager_user.id
        }
        response = self.client.post(url, data, format='json')
        # Assuming CanManageProject denies Employees from creating projects
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
