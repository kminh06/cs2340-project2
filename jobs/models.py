from django.conf import settings
from django.db import models

from profiles.models import Skill


class Job(models.Model):
    """A job posting. US-11: recruiters post/edit these."""

    class WorkType(models.TextChoices):
        REMOTE = "REMOTE", "Remote"
        ONSITE = "ONSITE", "On-site"
        HYBRID = "HYBRID", "Hybrid"

    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, blank=True, related_name="jobs")
    company = models.CharField(max_length=200)

    office_address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    work_type = models.CharField(max_length=10, choices=WorkType.choices, default=WorkType.ONSITE)
    visa_sponsorship = models.BooleanField(default=False)

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posted_jobs"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}"

    @property
    def salary_range_display(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        if self.salary_min:
            return f"${self.salary_min:,}+"
        return "Not specified"
