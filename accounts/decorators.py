"""Role-based access decorators for function-based views.

Use these on views that must only be reachable by one kind of user, e.g.:

    @job_seeker_required
    def apply_to_job(request, job_id):
        ...

For class-based views, use the equivalent mixins in ``accounts.mixins``.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import User


def _role_required(role, view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if request.user.role != role:
            raise PermissionDenied("You do not have access to this page.")
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped)


def job_seeker_required(view_func):
    """Restrict a view to authenticated users with the JOB_SEEKER role."""
    return _role_required(User.Role.JOB_SEEKER, view_func)


def recruiter_required(view_func):
    """Restrict a view to authenticated users with the RECRUITER role."""
    return _role_required(User.Role.RECRUITER, view_func)


def admin_required(view_func):
    """Restrict a view to authenticated users with the ADMIN role.

    Note: this checks our custom ``role`` field, not Django's
    ``is_staff``/``is_superuser``. Django admin (/admin/) uses the builtin
    staff/superuser permissions separately.
    """
    return _role_required(User.Role.ADMIN, view_func)
