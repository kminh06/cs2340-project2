from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .decorators import admin_required
from .forms import ManageUserForm, SignUpForm
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
    """US-21: Administrators view all users, filtered by search/role/status.

    Each row posts to ``update_user`` to change role or active status.
    """
    users = User.objects.all()
    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    status = request.GET.get("status", "")
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if role in User.Role.values:
        users = users.filter(role=role)
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)
    return render(request, "accounts/manage_users.html", {
        "users": users,
        "roles": User.Role.choices,
        "q": q,
        "role": role,
        "status": status,
    })


@require_POST
@admin_required
def update_user(request, user_id):
    """US-21: change a user's role and/or activate/deactivate their account.

    Admins cannot edit their own account here, so the site can never be
    left without an active administrator by accident.
    """
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, "You cannot change your own role or status.")
    else:
        form = ManageUserForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {target.username}.")
        else:
            messages.error(request, f"Could not update {target.username}.")
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("accounts:manage_users")
