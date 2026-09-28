from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import job_seeker_required
from jobs.models import Job

from .models import SavedJob


@job_seeker_required
def cart_detail(request):
    saved_jobs = SavedJob.objects.filter(
        seeker=request.user
    ).select_related("job").prefetch_related("job__skills")

    return render(
        request,
        "cart/cart_detail.html",
        {"saved_jobs": saved_jobs},
    )


@job_seeker_required
def add_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    saved_job, created = SavedJob.objects.get_or_create(
        seeker=request.user,
        job=job,
    )

    if created:
        messages.success(request, "Job added to your saved jobs.")
    else:
        messages.info(request, "You already saved this job.")

    return redirect("cart:cart_detail")


@job_seeker_required
def remove_job(request, job_id):
    SavedJob.objects.filter(
        seeker=request.user,
        job_id=job_id,
    ).delete()

    messages.success(request, "Job removed from your saved jobs.")

    return redirect("cart:cart_detail")