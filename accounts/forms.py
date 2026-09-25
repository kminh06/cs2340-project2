from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    """Registration form that lets a new user pick their role.

    Profile creation (headline/company/etc.) happens afterwards in the
    ``profiles`` app, not here.
    """

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[
            (User.Role.JOB_SEEKER, "Job Seeker"),
            (User.Role.RECRUITER, "Recruiter"),
        ],
        widget=forms.RadioSelect,
        help_text="Administrator accounts are created by existing admins, not via signup.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user
