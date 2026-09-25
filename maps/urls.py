from django.urls import path

from . import views

app_name = "maps"

urlpatterns = [
    path("jobs/", views.job_map, name="job_map"),
    path("jobs/data/", views.job_map_data, name="job_map_data"),
    path("applicants/", views.applicant_map, name="applicant_map"),
    path("applicants/data/", views.applicant_map_data, name="applicant_map_data"),
    path("jobs/<int:job_id>/pin/", views.job_location_pin, name="job_location_pin"),
]
