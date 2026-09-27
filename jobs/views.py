from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import recruiter_required

from .forms import JobForm, JobSearchForm
from .models import Job
from .services import search_jobs


def job_search(request):
    """US-2: Job seekers (and anyone) search/filter jobs by title, skills,
    location, salary range, remote/on-site/hybrid, and visa sponsorship.

    TODO(US-2): Bind ``JobSearchForm`` to ``request.GET``, and when valid
    call ``jobs.services.search_jobs(form.cleaned_data)`` to get the
    queryset. Render results in the template with pagination. Link each
    result to ``jobs:job_detail`` and to ``cart:add_job`` (US-10).
    """
    form = JobSearchForm(request.GET or None)
    if form.is_valid():
        jobs=search_jobs(form.cleaned_data)
    else:
        jobs = Job.objects.none()
    paginator=Paginator(jobs,10)
    page_num=request.GET.get("page")
    page_obj=paginator.get_page(page_num)
    copy_filter=request.GET.copy()
    copy_filter.pop("page",None)
    return render(request, "jobs/job_search.html", {"form": form, "jobs": page_obj, "page_obj": page_obj, "copy_filter":copy_filter.urlencode()},)


def job_detail(request, pk):
    """Show a single job posting.

    TODO: Once US-3 (one-click apply) is implemented in the applications
    app, link to it from this page. Also link to US-10 (add to cart).
    """
    job = get_object_or_404(Job, pk=pk)
    return render(request, "jobs/job_detail.html", {"job": job})


@recruiter_required
def job_list_mine(request):
    """Recruiter's list of their own postings (supports US-11 edit links).

    TODO(US-11): Add status filters (active/inactive) and a link to the
    applicant pipeline (applications:pipeline) and applicant map
    (maps:applicant_map) for each job.
    """
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, "jobs/job_list_mine.html", {"jobs": jobs})


@recruiter_required
def job_create(request):
    """US-11: Recruiters post a new job role."""
    job = Job(posted_by=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job posted.")
            return redirect("jobs:job_detail", pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form})


@recruiter_required
def job_edit(request, pk):
    """US-11: Recruiters edit an existing job role."""
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated.")
            return redirect("jobs:job_detail", pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form, "job": job})
