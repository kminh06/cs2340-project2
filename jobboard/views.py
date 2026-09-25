from django.shortcuts import redirect, render


def home(request):
    """Public landing page; sends logged-in users to their dashboard."""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return render(request, "home.html")
