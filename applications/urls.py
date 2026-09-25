from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("mine/", views.my_applications, name="my_applications"),
    path("apply/<int:job_id>/", views.apply_to_job, name="apply_to_job"),
    path("pipeline/", views.pipeline, name="pipeline"),
    path("pipeline/<int:job_id>/", views.pipeline, name="pipeline_for_job"),
    path("<int:application_id>/", views.applicant_detail, name="applicant_detail"),
]
