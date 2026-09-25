from django.conf import settings
from django.db import models

from jobs.models import Job


class SavedJob(models.Model):
    """US-10: a job a seeker has saved to their 'shopping cart' to compare
    or apply to later."""

    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Optional personal notes for comparison.")

    class Meta:
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(fields=["seeker", "job"], name="unique_saved_job_per_seeker")
        ]

    def __str__(self):
        return f"{self.seeker} saved {self.job}"
