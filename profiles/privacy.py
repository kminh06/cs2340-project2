"""US-5: single source of truth for what a recruiter may see on a seeker profile.

Every view/template that shows a ``JobSeekerProfile`` to a recruiter (candidate
search results, applicant detail, applicant map, pipeline) MUST go through
``get_visible_profile_data`` below instead of reading profile fields directly.
This keeps privacy enforcement in one place instead of scattered `if` checks.
"""
from dataclasses import dataclass


@dataclass
class VisibleProfileData:
    """A recruiter-safe view of a JobSeekerProfile.

    Fields are ``None``/empty when the seeker has hidden that section.
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
    """Return only the parts of ``profile`` the recruiter ``viewer`` may see.

    TODO(US-5): This is a working default (blanket on/off per section). Teams
    may extend it to support per-recruiter or per-company visibility rules,
    but any such change must still funnel through this function so there is
    one enforcement point.
    """
    if profile is None or not profile.is_public_to_recruiters:
        return VisibleProfileData(visible=False)

    data = VisibleProfileData(
        visible=True,
        headline=profile.headline,
        summary=profile.summary,
        skills=list(profile.skills.all()),
    )
    if profile.show_location:
        data.location_text = profile.location_text
    if profile.show_education:
        data.education_entries = list(profile.education_entries.all())
    if profile.show_experience:
        data.experience_entries = list(profile.experience_entries.all())
    if profile.show_links:
        data.links = list(profile.links.all())
    if profile.show_contact_info:
        data.contact_email = profile.user.email
    return data
