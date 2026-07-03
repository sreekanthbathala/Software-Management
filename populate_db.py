import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'software.settings')
django.setup()

from core.models import User, Project, Task, Training, Notification, Comment

def populate():
    print("Creating users...")
    hr_user, _ = User.objects.get_or_create(username='hr_admin', defaults={'password': 'password123', 'role': 'HR', 'email': 'hr@example.com'})
    manager1, _ = User.objects.get_or_create(username='manager_alice', defaults={'password': 'password123', 'role': 'Manager', 'email': 'alice@example.com'})
    emp1, _ = User.objects.get_or_create(username='emp_bob', defaults={'password': 'password123', 'role': 'Employee', 'email': 'bob@example.com'})
    emp2, _ = User.objects.get_or_create(username='emp_charlie', defaults={'password': 'password123', 'role': 'Employee', 'email': 'charlie@example.com'})
    instructor, _ = User.objects.get_or_create(username='instructor_dave', defaults={'password': 'password123', 'role': 'Instructor', 'email': 'dave@example.com'})

    print("Creating projects...")
    proj1, _ = Project.objects.get_or_create(
        name='Website Redesign',
        defaults={
            'description': 'Redesign the corporate website with a modern look.',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
            'manager': manager1,
            'status': 'In Progress'
        }
    )
    
    proj2, _ = Project.objects.get_or_create(
        name='Mobile App Launch',
        defaults={
            'description': 'Launch the new iOS and Android apps.',
            'start_date': date.today() + timedelta(days=5),
            'end_date': date.today() + timedelta(days=60),
            'manager': manager1,
            'status': 'Not Started'
        }
    )

    print("Creating tasks...")
    task1, _ = Task.objects.get_or_create(
        title='Design Mockups',
        defaults={
            'description': 'Create Figma mockups for the homepage.',
            'project': proj1,
            'created_by': manager1,
            'assigned_to': emp1,
            'due_date': date.today() + timedelta(days=7),
            'status': 'In Progress',
            'priority': 'High'
        }
    )

    task2, _ = Task.objects.get_or_create(
        title='Frontend Development',
        defaults={
            'description': 'Implement the homepage mockups using React.',
            'project': proj1,
            'created_by': manager1,
            'assigned_to': emp2,
            'due_date': date.today() + timedelta(days=14),
            'status': 'Pending',
            'priority': 'Medium'
        }
    )

    print("Creating trainings...")
    training1, _ = Training.objects.get_or_create(
        title='React Advanced Concepts',
        defaults={
            'description': 'Deep dive into hooks, context, and performance optimization.',
            'instructor': instructor,
            'date': date.today() + timedelta(days=10)
        }
    )
    training1.attendees.add(emp1, emp2)

    print("Creating comments and notifications...")
    Comment.objects.get_or_create(
        task=task1,
        author=emp1,
        content="I have started working on the mockups. Will share a draft soon."
    )

    Notification.objects.get_or_create(
        user=manager1,
        message="Bob has started working on the Design Mockups."
    )

    print("Dummy data added successfully!")

if __name__ == '__main__':
    populate()
