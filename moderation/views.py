import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

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


@admin_required
def job_moderation_list(request):
    """US-22: moderate/remove job posts.

    TODO(US-22): List all jobs (active and inactive) with a toggle/action to
    deactivate (set is_active=False) or permanently delete a posting that
    violates policy. Highlight jobs that have open Reports against them.
    """
    jobs = Job.objects.all()
    return render(request, "moderation/job_moderation_list.html", {"jobs": jobs})


@admin_required
def job_deactivate(request, job_id):
    """US-22: deactivate (soft-remove) a job post.

    TODO(US-22): On POST, set ``job.is_active = False`` and save; redirect
    back to job_moderation_list with a confirmation message.
    """
    job = get_object_or_404(Job, pk=job_id)
    return redirect("moderation:job_moderation_list")


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
