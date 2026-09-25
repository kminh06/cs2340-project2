from django.shortcuts import get_object_or_404, render

from accounts.decorators import job_seeker_required, recruiter_required
from jobs.models import Job

from . import services


@job_seeker_required
def job_recommendations(request):
    """US-6: show job recommendations based on the seeker's skills.

    TODO(US-6): Call ``services.recommend_jobs_for_seeker(request.user)`` and
    render the results like the job search page, with an explanation of why
    each job was recommended (e.g. matched skills).
    """
    jobs = services.recommend_jobs_for_seeker(request.user)
    return render(request, "recommendations/job_recommendations.html", {"jobs": jobs})


@recruiter_required
def candidate_recommendations(request, job_id):
    """US-17: show candidate recommendations for one of the recruiter's job
    postings.

    TODO(US-17): 404 if the job isn't owned by request.user. Call
    ``services.recommend_candidates_for_job(job)`` and render results using
    ``profiles.privacy.get_visible_profile_data`` for each candidate.
    """
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)
    candidates = services.recommend_candidates_for_job(job)
    return render(
        request,
        "recommendations/candidate_recommendations.html",
        {"job": job, "candidates": candidates},
    )
