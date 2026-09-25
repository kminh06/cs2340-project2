from django.conf import settings
from django.db import models


class Skill(models.Model):
    """A shared skill tag usable by both job seeker profiles and job postings.

    Shared model referenced via M2M from ``profiles.JobSeekerProfile`` and
    ``jobs.Job`` so skill-overlap scoring (US-6, US-17) can compare the two.
    """

    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobSeekerProfile(models.Model):
    """US-1: Job seeker profile with headline, skills, education, links.

    US-5: privacy fields below control what a recruiter can see; the single
    source of truth for enforcing that is ``profiles.privacy.get_visible_profile_fields``
    (see privacy.py), which every recruiter-facing view must call instead of
    reading these flags directly.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seeker_profile",
    )
    headline = models.CharField(max_length=150, blank=True)
    summary = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="seeker_profiles")

    location_text = models.CharField(
        max_length=255, blank=True, help_text="Free-text city/region, e.g. 'Atlanta, GA'."
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # --- US-5 privacy settings ---
    is_public_to_recruiters = models.BooleanField(
        default=True, help_text="If off, recruiters cannot find or view this profile at all."
    )
    show_contact_info = models.BooleanField(default=False)
    show_education = models.BooleanField(default=True)
    show_experience = models.BooleanField(default=True)
    show_links = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Seeker profile: {self.user.username}"


class Education(models.Model):
    """One education entry for a job seeker (US-1)."""

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="education_entries"
    )
    school = models.CharField(max_length=200)
    degree = models.CharField(max_length=150, blank=True)
    field_of_study = models.CharField(max_length=150, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if in progress.")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.school} - {self.degree}" if self.degree else self.school


class Experience(models.Model):
    """One work experience entry for a job seeker (US-1)."""

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="experience_entries"
    )
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=150)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} at {self.company}"


class Link(models.Model):
    """An external link (portfolio, GitHub, LinkedIn, etc.) for US-1."""

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="links"
    )
    label = models.CharField(max_length=100, help_text="e.g. GitHub, Portfolio, LinkedIn")
    url = models.URLField()

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return f"{self.label}: {self.url}"


class RecruiterProfile(models.Model):
    """Recruiter-side profile: company info shown alongside job postings."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruiter_profile",
    )
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)
    company_location = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"
