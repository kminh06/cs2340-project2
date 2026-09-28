from django import forms

from profiles.models import Skill

from .models import Job


YES_NO_CHOICES = [("True", "Yes"), ("False", "No")]


def _yes_no_field(label):
    """A Yes/No dropdown that saves to a BooleanField as True/False."""
    return forms.TypedChoiceField(
        label=label,
        choices=YES_NO_CHOICES,
        coerce=lambda v: v == "True",
        widget=forms.Select,
    )


class JobForm(forms.ModelForm):
    """US-11: post/edit a job role.

    ``skills`` is a hidden comma-separated field. The job form page fills it
    in with JavaScript from the skill chips the recruiter adds and removes,
    the same way the job seeker profile page does.

    Latitude/longitude are not editable here. They stay on the model for the
    job map (US-18) and are set from the map pin page instead.
    """

    skills = forms.CharField(required=False, widget=forms.HiddenInput)
    visa_sponsorship = _yes_no_field("Visa sponsorship")
    is_active = _yes_no_field("Is active")

    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "company",
            "office_address",
            "salary_min",
            "salary_max",
            "work_type",
            "visa_sponsorship",
            "is_active",
        ]
        labels = {
            "office_address": "Location",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "office_address": forms.TextInput(attrs={"placeholder": "e.g. Atlanta, GA"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show the dropdowns pre-set to the job's current values ("Yes" for a
        # new job's is_active, "No" for a new job's visa_sponsorship).
        self.initial["visa_sponsorship"] = str(bool(self.instance.visa_sponsorship))
        self.initial["is_active"] = str(bool(self.instance.is_active))
        if self.instance and self.instance.pk:
            self.fields["skills"].initial = ", ".join(
                self.instance.skills.values_list("name", flat=True)
            )

    def save(self, commit=True):
        job = super().save(commit=commit)
        if commit:
            self._save_skills(job)
        return job

    def _save_skills(self, job):
        names = [n.strip() for n in self.cleaned_data.get("skills", "").split(",") if n.strip()]
        skills = []
        for name in names:
            skill, _ = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name})
            skills.append(skill)
        job.skills.set(skills)


class JobSearchForm(forms.Form):
    """US-2: search/filter jobs by title, skills, location, salary, work
    type, and visa sponsorship."""

    title = forms.CharField(required=False)
    skills = forms.CharField(
        required=False, help_text="Comma-separated skills, e.g. 'Python, SQL'"
    )
    location = forms.CharField(required=False)
    salary_min = forms.IntegerField(required=False, min_value=0)
    salary_max = forms.IntegerField(required=False, min_value=0)
    work_type = forms.ChoiceField(
        required=False, choices=[("", "Any")] + list(Job.WorkType.choices)
    )
    visa_sponsorship = forms.BooleanField(required=False)
