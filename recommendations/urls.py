from django.urls import path

from . import views

app_name = "recommendations"

urlpatterns = [
    path("jobs/", views.job_recommendations, name="job_recommendations"),
    path("candidates/<int:job_id>/", views.candidate_recommendations, name="candidate_recommendations"),
]
