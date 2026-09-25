from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render

from .decorators import admin_required
from .forms import SignUpForm
from .models import User


def signup(request):
    """Register a new Job Seeker or Recruiter account.

    Fully implemented (not a stub) so the team can log in and test other
    features immediately. Admin accounts are not self-service; create them
    via ``createsuperuser`` + the Django admin, or via US-21 tooling.
    """
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            if user.role == User.Role.JOB_SEEKER:
                return redirect("profiles:seeker_profile_edit")
            return redirect("profiles:recruiter_profile_edit")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def dashboard(request):
    """Landing page after login; routes the user to a role-appropriate view.

    Fully implemented as a simple router/hub page.
    """
    return render(request, "accounts/dashboard.html")


@admin_required
def manage_users(request):
    """US-21: Administrators view/manage all users and can change roles.

    TODO(US-21): List all users with search/filter by role and active status.
    Add actions to promote/demote roles, deactivate accounts, and reset
    passwords. Consider a ModelForm for inline role editing.
    """
    users = User.objects.all()
    return render(request, "accounts/manage_users.html", {"users": users})
