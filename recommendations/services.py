"""Recommendation logic, kept out of views per project convention.

Both functions currently use a simple skill-overlap score as a placeholder.
Replace with a smarter algorithm (weighting, location, salary fit, etc.) as
time allows -- the view-level call sites should not need to change.
"""
from jobs.models import Job
from profiles.models import JobSeekerProfile


def _skill_overlap_score(skills_a, skills_b) -> int:
    """Count of skills shared between two iterables of Skill objects."""
    ids_a = {s.id for s in skills_a}
    ids_b = {s.id for s in skills_b}
    return len(ids_a & ids_b)


def recommend_jobs_for_seeker(user, limit=10):
    """US-6: recommend active jobs to a job seeker based on skill overlap.

    TODO(US-6): Placeholder scoring only counts shared Skill rows between the
    seeker's profile and each job. Consider factoring in location/commute
    radius (US-8/US-9), salary expectations, and work_type preference once
    those are captured on the profile.
    """
    try:
        profile = user.seeker_profile
    except JobSeekerProfile.DoesNotExist:
        return []

    seeker_skills = list(profile.skills.all())
    if not seeker_skills:
        return []

    scored = []
    for job in Job.objects.filter(is_active=True).prefetch_related("skills"):
        score = _skill_overlap_score(seeker_skills, job.skills.all())
        if score > 0:
            scored.append((score, job))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [job for _score, job in scored[:limit]]


def recommend_candidates_for_job(job, limit=10):
    """US-17: recommend candidates to a recruiter for a given job posting,
    based on skill overlap.

    TODO(US-17): Placeholder scoring only counts shared Skill rows. Consider
    only surfacing candidates who are ``is_public_to_recruiters`` (US-5,
    already filtered below) and who haven't already applied. Must route any
    profile fields shown through ``profiles.privacy.get_visible_profile_data``.
    """
    job_skills = list(job.skills.all())
    if not job_skills:
        return []

    scored = []
    qs = JobSeekerProfile.objects.filter(is_public_to_recruiters=True).prefetch_related("skills")
    for profile in qs:
        score = _skill_overlap_score(job_skills, profile.skills.all())
        if score > 0:
            scored.append((score, profile))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [profile for _score, profile in scored[:limit]]
