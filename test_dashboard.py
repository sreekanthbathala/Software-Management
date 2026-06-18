import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'software.settings')
django.setup()

from rest_framework.test import APIClient
from core.models import User

try:
    client = APIClient()
    user = User.objects.get(username='aditi_hr')
    client.force_authenticate(user=user)
    response = client.get('/api/dashboard/')
    print("STATUS:", response.status_code)
    
    # If it's a 500, we should see why the Django exception occurred.
    # We can also simulate the view call manually to see the exact traceback.
    from core.views import DashboardViewSet
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('/api/dashboard/')
    request.user = user
    view = DashboardViewSet.as_view({'get': 'list'})
    response = view(request)
    print("DIRECT VIEW STATUS:", response.status_code)
    print("KEYS:", response.data.keys())
    print("ALL DATA:", response.data)

except Exception as e:
    traceback.print_exc()
