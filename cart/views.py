from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import job_seeker_required
from jobs.models import Job

from .models import SavedJob


@job_seeker_required
def cart_detail(request):
    """US-10: view saved jobs side-by-side for comparison before applying.

    TODO(US-10): Render saved jobs in a comparison-friendly layout (table of
    salary/work_type/location/skills). Link each row to
    ``applications:apply_to_job`` and to ``cart:remove_job``.
    """
    saved_jobs = SavedJob.objects.filter(seeker=request.user)
    return render(request, "cart/cart_detail.html", {"saved_jobs": saved_jobs})


@job_seeker_required
def add_job(request, job_id):
    """US-10: add a job to the seeker's saved-jobs cart.

    TODO(US-10): ``get_or_create(seeker=request.user, job=job)`` and redirect
    back to the referring page (job detail or search results) with a
    success message.
    """
    job = get_object_or_404(Job, pk=job_id)
    return redirect("cart:cart_detail")


@job_seeker_required
def remove_job(request, job_id):
    """US-10: remove a job from the saved-jobs cart.

    TODO(US-10): Delete the matching SavedJob (if any) for request.user and
    redirect back to cart:cart_detail with a confirmation message.
    """
    return redirect("cart:cart_detail")
