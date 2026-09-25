from django import forms

from .models import Application


class ApplicationForm(forms.ModelForm):
    """US-3: one-click apply with a tailored note."""

    class Meta:
        model = Application
        fields = ["tailored_note"]
        widgets = {
            "tailored_note": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Why are you a great fit for this role?"}
            )
        }


class ApplicationStatusForm(forms.ModelForm):
    """US-13: recruiter moves an applicant to a new pipeline stage."""

    class Meta:
        model = Application
        fields = ["status"]
