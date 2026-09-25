from django import forms

from profiles.models import Skill

from .models import Job


class JobForm(forms.ModelForm):
    """US-11: post/edit a job role."""

    skills = forms.CharField(
        required=False, help_text="Comma-separated list of skills, e.g. 'Python, SQL, React'."
    )

    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "company",
            "office_address",
            "latitude",
            "longitude",
            "salary_min",
            "salary_max",
            "work_type",
            "visa_sponsorship",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
