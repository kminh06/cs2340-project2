from django import forms

from .models import Report


class ReportForm(forms.ModelForm):
    """File a report against a user or a job posting (feeds US-24)."""

    class Meta:
        model = Report
        fields = ["target_user", "target_job", "reason"]
        widgets = {
            "target_user": forms.HiddenInput(),
            "target_job": forms.HiddenInput(),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }


class ReportResolutionForm(forms.ModelForm):
    """US-24: admin updates a report's status after review."""

    class Meta:
        model = Report
        fields = ["status"]
