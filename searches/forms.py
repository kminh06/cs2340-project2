from django import forms

from .models import SavedSearch


class SavedSearchForm(forms.ModelForm):
    """US-16: save a recruiter's candidate-search filters for later reuse
    and match notifications."""

    class Meta:
        model = SavedSearch
        fields = ["name", "filters"]
        widgets = {"filters": forms.HiddenInput()}
