from django import forms
from django.forms import inlineformset_factory

from .models import Education, Experience, JobSeekerProfile, Link, RecruiterProfile, Skill


class JobSeekerProfileForm(forms.ModelForm):
    """US-1 core profile fields + US-5 privacy toggles."""

    skills = forms.CharField(
        required=False,
        help_text="Comma-separated list of skills, e.g. 'Python, SQL, React'.",
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            "headline",
            "summary",
            "location_text",
            "latitude",
            "longitude",
            "is_public_to_recruiters",
            "show_contact_info",
            "show_education",
            "show_experience",
            "show_links",
            "show_location",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["skills"].initial = ", ".join(
                self.instance.skills.values_list("name", flat=True)
            )

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            self._save_skills(profile)
        return profile

    def _save_skills(self, profile):
        names = [n.strip() for n in self.cleaned_data.get("skills", "").split(",") if n.strip()]
        skills = []
        for name in names:
            skill, _ = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name})
            skills.append(skill)
        profile.skills.set(skills)


EducationFormSet = inlineformset_factory(
    JobSeekerProfile,
    Education,
    fields=["school", "degree", "field_of_study", "start_date", "end_date", "description"],
    extra=1,
    can_delete=True,
    widgets={
        "start_date": forms.DateInput(attrs={"type": "date"}),
        "end_date": forms.DateInput(attrs={"type": "date"}),
    },
)

ExperienceFormSet = inlineformset_factory(
    JobSeekerProfile,
    Experience,
    fields=[
        "company",
        "title",
        "location",
        "start_date",
        "end_date",
        "is_current",
        "description",
    ],
    extra=1,
    can_delete=True,
    widgets={
        "start_date": forms.DateInput(attrs={"type": "date"}),
        "end_date": forms.DateInput(attrs={"type": "date"}),
    },
)

LinkFormSet = inlineformset_factory(
    JobSeekerProfile,
    Link,
    fields=["label", "url"],
    extra=1,
    can_delete=True,
)


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ["company_name", "company_website", "company_description", "company_location"]
        widgets = {
            "company_description": forms.Textarea(attrs={"rows": 4}),
        }
