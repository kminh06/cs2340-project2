"""Role-based access mixins for class-based views.

Mirrors ``accounts.decorators`` for CBVs, e.g.:

    class PostJobView(RecruiterRequiredMixin, CreateView):
        ...
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import User


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Base mixin: subclasses set ``required_role``."""

    required_role = None

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role == self.required_role
        )


class JobSeekerRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.JOB_SEEKER


class RecruiterRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.RECRUITER


class AdminRoleRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.ADMIN
