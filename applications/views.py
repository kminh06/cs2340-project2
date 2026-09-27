from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from accounts.decorators import job_seeker_required, recruiter_required
from jobs.models import Job
from profiles.privacy import get_visible_profile_data

from .forms import ApplicationForm
from .models import Application


@job_seeker_required
def apply_to_job(request, job_id):
    """US-3: One-click apply with a tailored note."""
    job = get_object_or_404(Job, pk=job_id)
    if Application.objects.filter(job=job,applicant=request.user).exists():
        messages.warning(request, "You already applied for this job.")
        return redirect("applications:my_applications")
    if request.method=="POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application=form.save(commit=False)
            application.job=job
            application.applicant=request.user
            application.save()
            messages.success(request, "Your application was successfully submitted.")
            return redirect("applications:my_applications")
    else:
        form = ApplicationForm()
    return render(request, "applications/apply.html", {"job": job, "form": form})


@job_seeker_required
def my_applications(request):
    """US-4: Track application status (Applied -> Review -> Interview ->
    Offer -> Closed).

    TODO(US-4): Query ``Application.objects.filter(applicant=request.user)``
    and group/sort by status for a clear timeline view.
    """
    applications = Application.objects.filter(applicant=request.user)
    return render(request, "applications/my_applications.html", {"applications": applications})


@recruiter_required
def pipeline(request, job_id=None):
    """US-13: Recruiters organize applicants in a Kanban pipeline by stage.

    TODO(US-13): Build a board with one column per ``Application.Status``.
    Support drag-and-drop or a simple per-card status dropdown
    (``ApplicationStatusForm``) that POSTs back to update the stage. Scope
    applications to jobs owned by ``request.user`` (posted_by=request.user).
    """
    applications = Application.objects.filter(job__posted_by=request.user)
    return render(request, "applications/pipeline.html", {"applications": applications})


@recruiter_required
def applicant_detail(request, application_id):
    """US-20: Review a candidate's profile + application details in one place.

    TODO(US-20): Load the Application (404 if its job isn't owned by
    request.user), then use
    ``profiles.privacy.get_visible_profile_data(applicant.seeker_profile,
    viewer=request.user)`` to render only what the seeker's privacy settings
    (US-5) allow, alongside the tailored note, status, and status-change
    history for this application.
    """
    application = get_object_or_404(
        Application, pk=application_id, job__posted_by=request.user
    )
    seeker_profile = getattr(application.applicant, "seeker_profile", None)
    visible_profile = get_visible_profile_data(seeker_profile, viewer=request.user)
    return render(
        request,
        "applications/applicant_detail.html",
        {"application": application, "visible_profile": visible_profile},
    )
