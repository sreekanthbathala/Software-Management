from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'trainings', views.TrainingViewSet, basename='training')
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'activity-logs', views.ActivityLogViewSet, basename='activitylog')
router.register(r'task-attachments', views.TaskAttachmentViewSet, basename='taskattachment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Auth endpoints for the frontend
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/auth/create-user/', views.CreateUserView.as_view(), name='create_user'),
    
    path('api/current-user/', views.CurrentUserView.as_view(), name='current_user'),
    
    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Frontend Templates
    path('', views.home_view, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('dashboard/', views.dashboard_page, name='dashboard_page'),
    path('dashboard/projects/', views.projects_page, name='projects_page'),
    path('dashboard/tasks/', views.tasks_page, name='tasks_page'),
    path('dashboard/trainings/', views.trainings_page, name='trainings_page'),

    path('dashboard/create-user/', views.create_user_page, name='create_user_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
