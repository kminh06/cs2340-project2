from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import recruiter_required

from .forms import EmailCandidateForm, MessageForm
from .models import Conversation

User = get_user_model()


@login_required
def inbox(request):
    """US-14: list the current user's conversations.

    TODO: Filter ``Conversation.objects.filter(participants=request.user)``
    and show the latest message + unread count per conversation.
    """
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, "messaging/inbox.html", {"conversations": conversations})


@login_required
def conversation_detail(request, conversation_id):
    """US-14: view a message thread and send a new message.

    TODO(US-14): 404 if request.user is not a participant. On POST, bind
    ``MessageForm``, save with ``sender=request.user`` and
    ``conversation=conversation``. Consider marking messages as read here.
    """
    conversation = get_object_or_404(
        Conversation, pk=conversation_id, participants=request.user
    )
    form = MessageForm()
    return render(
        request,
        "messaging/conversation_detail.html",
        {"conversation": conversation, "form": form},
    )


@recruiter_required
def email_candidate(request, candidate_id):
    """US-15: recruiters email a candidate through the platform.

    TODO(US-15): On valid POST, call Django's ``send_mail(subject, body,
    settings.DEFAULT_FROM_EMAIL, [candidate.email])``. In dev this uses the
    console email backend (see settings.EMAIL_BACKEND) so messages print to
    the runserver console instead of actually sending. Consider logging the
    email as a Message in a Conversation too, so it shows up in-platform.
    """
    candidate = get_object_or_404(User, pk=candidate_id, role=User.Role.JOB_SEEKER)
    form = EmailCandidateForm()
    return render(request, "messaging/email_candidate.html", {"candidate": candidate, "form": form})
