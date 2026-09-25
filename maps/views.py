from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from accounts.decorators import job_seeker_required, recruiter_required
from applications.models import Application
from jobs.models import Job

from . import utils


@job_seeker_required
def job_map(request):
    """US-7: interactive map of job postings.
    US-8: filter map jobs by distance from the seeker's current location.
    US-9: let the seeker set a preferred commute radius (e.g. 10 miles).

    This renders the Leaflet map shell; ``job_map_data`` below supplies the
    marker JSON via fetch().

    TODO(US-7/8/9): Add controls for the seeker's current location (browser
    geolocation API) and a radius slider, and pass them as query params to
    ``maps:job_map_data``.
    """
    return render(request, "maps/job_map.html")


@job_seeker_required
def job_map_data(request):
    """JSON endpoint of job map points for US-7/8/9.

    TODO(US-7/8/9): Read ``lat``, ``lng``, and ``radius`` from
    request.GET (radius in miles). If present, use
    ``maps.utils.filter_by_radius`` to narrow the queryset before building
    the response below. Currently returns ALL active jobs with coordinates,
    unfiltered.
    """
    jobs = Job.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False)
    points = [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "lat": float(job.latitude),
            "lng": float(job.longitude),
            "url": f"/jobs/{job.id}/",
        }
        for job in jobs
    ]
    return JsonResponse({"points": points})


@recruiter_required
def applicant_map(request):
    """US-19: see applicant clusters by location on a map.

    Renders the Leaflet + markercluster map shell; ``applicant_map_data``
    below supplies marker JSON via fetch().

    TODO(US-19): Add a job filter (dropdown of the recruiter's own postings)
    so they can view clusters per-job or across all their jobs.
    """
    return render(request, "maps/applicant_map.html")


@recruiter_required
def applicant_map_data(request):
    """JSON endpoint of applicant map points for US-19.

    TODO(US-19): Scope to jobs owned by request.user, optionally filtered by
    a ``job`` query param. Must respect US-5 privacy: only include an
    applicant's location if their JobSeekerProfile has
    ``is_public_to_recruiters`` and ``show_location`` set (see
    profiles.privacy.get_visible_profile_data) -- do not leak hidden
    locations onto the map.
    """
    applications = Application.objects.filter(job__posted_by=request.user).select_related(
        "applicant__seeker_profile"
    )
    points = []
    for application in applications:
        profile = getattr(application.applicant, "seeker_profile", None)
        if profile and profile.latitude is not None and profile.longitude is not None:
            points.append(
                {
                    "application_id": application.id,
                    "applicant": application.applicant.username,
                    "job": application.job.title,
                    "lat": float(profile.latitude),
                    "lng": float(profile.longitude),
                }
            )
    return JsonResponse({"points": points})


@recruiter_required
def job_location_pin(request, job_id):
    """US-18: pin a job's office location on a map when posting/editing it.

    TODO(US-18): Render a small Leaflet map with a draggable marker on the
    job form (jobs:job_create / jobs:job_edit) that writes back into the
    latitude/longitude fields, rather than as a separate page. This view is
    a placeholder location for that logic/documentation.
    """
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)
    return render(request, "maps/job_location_pin.html", {"job": job})
