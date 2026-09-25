from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("me/", views.seeker_profile_edit, name="seeker_profile_edit"),
    path("me/company/", views.recruiter_profile_edit, name="recruiter_profile_edit"),
    path("candidates/", views.candidate_search, name="candidate_search"),
]
