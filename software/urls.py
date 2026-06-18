
from django.contrib import admin
from django.core.checks import templates
from django.urls import include, path
from core import views
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'trainings', views.TrainingViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')
router.register(r'leave-requests', views.LeaveRequestViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Template pages
    path('', views.home_view, name='home'),
    path('login/', views.login_page, name='login'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('dashboard/projects/', views.projects_page, name='projects'),
    path('dashboard/tasks/', views.tasks_page, name='tasks'),
    path('dashboard/trainings/', views.trainings_page, name='trainings'),
    path('dashboard/leave-requests/', views.leave_requests_page, name='leave-requests'),
    path('dashboard/create-user/', views.create_user_page, name='create-user'),
]
