from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import job_seeker_required, recruiter_required

from .forms import (
    EducationFormSet,
    ExperienceFormSet,
    JobSeekerProfileForm,
    LinkFormSet,
    RecruiterProfileForm,
)
from .models import JobSeekerProfile, RecruiterProfile


@job_seeker_required
def seeker_profile_edit(request):
    """US-1: create/edit the job seeker's profile (headline, skills,
    education, experience, links) and US-5 privacy toggles.

    Fully implemented so the team can log in and test other features.
    """
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = JobSeekerProfileForm(request.POST, instance=profile)
        education_fs = EducationFormSet(request.POST, instance=profile, prefix="edu")
        experience_fs = ExperienceFormSet(request.POST, instance=profile, prefix="exp")
        link_fs = LinkFormSet(request.POST, instance=profile, prefix="link")

        if all(
            f.is_valid() for f in (form, education_fs, experience_fs, link_fs)
        ):
            form.save()
            education_fs.save()
            experience_fs.save()
            link_fs.save()
            messages.success(request, "Profile updated.")
            return redirect("profiles:seeker_profile_edit")
    else:
        form = JobSeekerProfileForm(instance=profile)
        education_fs = EducationFormSet(instance=profile, prefix="edu")
        experience_fs = ExperienceFormSet(instance=profile, prefix="exp")
        link_fs = LinkFormSet(instance=profile, prefix="link")

    return render(
        request,
        "profiles/seeker_profile_edit.html",
        {
            "form": form,
            "education_fs": education_fs,
            "experience_fs": experience_fs,
            "link_fs": link_fs,
        },
    )


@recruiter_required
def recruiter_profile_edit(request):
    """Create/edit the recruiter's company profile.

    Fully implemented so the team can log in and test other features.
    """
    profile, _ = RecruiterProfile.objects.get_or_create(
        user=request.user, defaults={"company_name": ""}
    )

    if request.method == "POST":
        form = RecruiterProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated.")
            return redirect("profiles:recruiter_profile_edit")
    else:
        form = RecruiterProfileForm(instance=profile)

    return render(request, "profiles/recruiter_profile_edit.html", {"form": form})


@recruiter_required
def candidate_search(request):
    """US-12: Recruiters search candidates by skills, location, projects.

    TODO(US-12): Build a filter form (skills multi-select, location/radius
    reusing maps.utils.haversine_distance, keyword search over profile
    summary/experience). Results must be filtered through
    profiles.privacy.get_visible_profile_data so hidden profiles/fields never
    leak. Consider pagination for large result sets.
    """
    candidates = JobSeekerProfile.objects.filter(is_public_to_recruiters=True)
    return render(request, "profiles/candidate_search.html", {"candidates": candidates})
