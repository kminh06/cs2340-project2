from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import recruiter_required

from .models import Notification, SavedSearch


@recruiter_required
def saved_search_list(request):
    """US-16: view saved candidate searches.

    TODO(US-16): List ``SavedSearch.objects.filter(recruiter=request.user)``
    with a link to re-run each search (pass filters back to
    profiles:candidate_search as query params) and a delete action.
    """
    saved_searches = SavedSearch.objects.filter(recruiter=request.user)
    return render(request, "searches/saved_search_list.html", {"saved_searches": saved_searches})


@recruiter_required
def saved_search_create(request):
    """US-16: save the current candidate-search filters.

    TODO(US-16): Accept the current filter params (from
    profiles:candidate_search's query string), bind ``SavedSearchForm``, and
    save with recruiter=request.user. A periodic task or signal should later
    check for new matching candidates and create Notification objects.
    """
    return redirect("searches:saved_search_list")


@recruiter_required
def notification_list(request):
    """US-16/US-17: view notifications (e.g. new candidate matches).

    TODO: List ``Notification.objects.filter(user=request.user)`` ordered
    newest-first, and add an action to mark as read.
    """
    notifications = Notification.objects.filter(user=request.user)
    return render(request, "searches/notification_list.html", {"notifications": notifications})
