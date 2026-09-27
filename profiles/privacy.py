"""US-5: single source of truth for what a recruiter may see on a seeker profile.

NOT IMPLEMENTED YET. Right now every recruiter sees every profile in full, so
``get_visible_profile_data`` returns everything. It exists so that recruiter-
facing views (candidate search, applicant detail, applicant map, pipeline,
candidate recommendations) already go through one function, and US-5 can be
added here later without touching each view.

TODO(US-5):
  1. Add privacy fields to ``profiles.models.JobSeekerProfile`` plus a
     migration, for example:
       is_public_to_recruiters, show_contact_info, show_education,
       show_experience, show_links, show_location  (BooleanFields)
  2. Add those fields to ``JobSeekerProfileForm`` and a "Privacy" section with
     checkboxes to ``seeker_profile_edit.html``.
  3. Fill in the checks marked below, and filter hidden profiles out of the
     querysets in ``profiles.views.candidate_search``,
     ``recommendations.services.recommend_candidates_for_job`` and
     ``maps.views.applicant_map_data``.
"""
from dataclasses import dataclass


@dataclass
class VisibleProfileData:
    """A recruiter-safe view of a JobSeekerProfile.

    Once US-5 is implemented, fields are empty when the seeker hid that section.
    """

    visible: bool
    headline: str = ""
    summary: str = ""
    skills: list = None
    location_text: str = ""
    education_entries: list = None
    experience_entries: list = None
    links: list = None
    contact_email: str = ""


def get_visible_profile_data(profile, viewer=None) -> VisibleProfileData:
    """Return the parts of ``profile`` the recruiter ``viewer`` may see.

    Currently returns everything (US-5 not implemented yet).
    """
    if profile is None:
        return VisibleProfileData(visible=False)

    # TODO(US-5): return VisibleProfileData(visible=False) when the seeker's
    # profile is hidden from recruiters.
    data = VisibleProfileData(
        visible=True,
        headline=profile.headline,
        summary=profile.summary,
        skills=list(profile.skills.all()),
    )
    # TODO(US-5): wrap each of these in the matching show_* check.
    data.location_text = profile.location_text
    data.education_entries = list(profile.education_entries.all())
    data.experience_entries = list(profile.experience_entries.all())
    data.links = list(profile.links.all())
    data.contact_email = profile.user.email
    return data
