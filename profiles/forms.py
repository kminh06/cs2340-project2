from django import forms
from django.forms import inlineformset_factory

from .models import Education, Experience, JobSeekerProfile, Link, RecruiterProfile, Skill


class JobSeekerProfileForm(forms.ModelForm):
    """US-1 core profile fields.

    ``skills`` is a hidden comma-separated field. The profile page fills it
    in with JavaScript from the skill chips the user adds and removes.
    """

    skills = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = JobSeekerProfile
        fields = [
            "headline",
            "summary",
            "location_text",
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
    # Exactly one education box per profile.
    extra=1,
    max_num=1,
    validate_max=True,
    can_delete=False,
    widgets={
        "start_date": forms.DateInput(attrs={"type": "date"}),
        "end_date": forms.DateInput(attrs={"type": "date"}),
        "description": forms.Textarea(attrs={"rows": 3}),
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
    # Rows are added in the browser with the + button (see seeker_profile_edit.html).
    extra=0,
    can_delete=True,
    widgets={
        "start_date": forms.DateInput(attrs={"type": "date"}),
        "end_date": forms.DateInput(attrs={"type": "date"}),
        "description": forms.Textarea(attrs={"rows": 3}),
    },
)

LinkFormSet = inlineformset_factory(
    JobSeekerProfile,
    Link,
    fields=["label", "url"],
    # Rows are added in the browser with the + button (see seeker_profile_edit.html).
    extra=0,
    can_delete=True,
)


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ["company_name", "company_website", "company_description", "company_location"]
        widgets = {
            "company_description": forms.Textarea(attrs={"rows": 4}),
        }
