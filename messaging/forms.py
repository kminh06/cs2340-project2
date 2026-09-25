from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    """US-14: send a message within a conversation."""

    class Meta:
        model = Message
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a message..."})}


class EmailCandidateForm(forms.Form):
    """US-15: email a candidate through the platform via Django's send_mail."""

    subject = forms.CharField(max_length=200)
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))
