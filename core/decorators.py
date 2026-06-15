from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            elif not request.user.is_authenticated:
                return redirect('login')  # Redirect to login page if not authenticated
            else:
                raise PermissionDenied  # Raise 403 error if authenticated but not authorized
        return _wrapped_view
    return decorator