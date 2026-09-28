import csv

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from jobs.models import Job

from .forms import ReportForm
from .models import Report


def file_report(request):
    """Let any signed-in user file a report against a user or job posting.

    This feeds the admin queue reviewed in US-24. Not itself numbered as a
    user story, but required plumbing for one.

    TODO: Bind ``ReportForm`` to POST data, set ``reporter=request.user``,
    and redirect with a "thanks, we'll review this" message. The
    target_user/target_job should be passed in via query params or hidden
    fields from the reporting page (e.g. a "Report" button on a job or
    profile page).
    """
    form = ReportForm(initial={
        "target_user": request.GET.get("user"),
        "target_job": request.GET.get("job"),
    })
    return render(request, "moderation/file_report.html", {"form": form})


@admin_required
def report_list(request):
    """US-24: review reports about users/job postings before taking action.

    TODO(US-24): Add filters by status (OPEN/UNDER_REVIEW/RESOLVED/DISMISSED)
    and by target type (user vs job). Link each row to report_detail.
    """
    reports = Report.objects.all()
    return render(request, "moderation/report_list.html", {"reports": reports})


@admin_required
def report_detail(request, report_id):
    """US-24: review a single report and take action (resolve/dismiss),
    which may include deactivating the target job (US-22) or the target
    user's account.

    TODO(US-24): Bind ``ReportResolutionForm`` for status changes. Consider
    adding quick actions here: deactivate target_job (sets Job.is_active =
    False) or deactivate target_user (sets User.is_active = False).
    """
    report = get_object_or_404(Report, pk=report_id)
    return render(request, "moderation/report_detail.html", {"report": report})


OPEN_REPORT_STATUSES = [Report.Status.OPEN, Report.Status.UNDER_REVIEW]


@admin_required
def job_moderation_list(request):
    """US-22: Administrators view all job posts (active and inactive),
    filtered by search/status/reported, with jobs that have open reports
    highlighted.

    Each row posts to ``job_deactivate``/``job_reactivate``/``job_delete``.
    """
    jobs = Job.objects.select_related("posted_by").annotate(
        open_reports=Count(
            "reports_against", filter=Q(reports_against__status__in=OPEN_REPORT_STATUSES)
        )
    )
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    reported = request.GET.get("reported", "")
    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) | Q(company__icontains=q) | Q(posted_by__username__icontains=q)
        )
    if status == "active":
        jobs = jobs.filter(is_active=True)
    elif status == "inactive":
        jobs = jobs.filter(is_active=False)
    if reported:
        jobs = jobs.filter(open_reports__gt=0)
    return render(request, "moderation/job_moderation_list.html", {
        "jobs": jobs,
        "q": q,
        "status": status,
        "reported": reported,
    })


def _back_to_list(request):
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("moderation:job_moderation_list")


def _set_job_active(request, job_id, active):
    job = get_object_or_404(Job, pk=job_id)
    job.is_active = active
    job.save(update_fields=["is_active", "updated_at"])
    verb = "Reactivated" if active else "Deactivated"
    messages.success(request, f'{verb} "{job.title}".')
    return _back_to_list(request)


@require_POST
@admin_required
def job_deactivate(request, job_id):
    """US-22: deactivate (soft-remove) a job post so it no longer appears in
    search, recommendations, or the map, and can't be applied to."""
    return _set_job_active(request, job_id, False)


@require_POST
@admin_required
def job_reactivate(request, job_id):
    """US-22: undo a deactivation that turned out to be a mistake."""
    return _set_job_active(request, job_id, True)


@require_POST
@admin_required
def job_delete(request, job_id):
    """US-22: permanently delete a posting that violates policy (spam/abuse).

    This also deletes its applications and reports, so prefer deactivating
    unless the post should be gone entirely.
    """
    job = get_object_or_404(Job, pk=job_id)
    title = job.title
    job.delete()
    messages.success(request, f'Deleted "{title}".')
    return _back_to_list(request)


@admin_required
def export_csv(request):
    """US-23: export data as CSV for reporting.

    TODO(US-23): This currently exports only the Users table as a
    demonstration. Add query params or separate endpoints to export Jobs,
    Applications, and Reports too (whatever the team needs for reporting).
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users_export.csv"'

    from accounts.models import User

    writer = csv.writer(response)
    writer.writerow(["id", "username", "email", "role", "is_active", "date_joined"])
    for user in User.objects.all().values_list(
        "id", "username", "email", "role", "is_active", "date_joined"
    ):
        writer.writerow(user)

    return response
