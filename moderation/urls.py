from django.urls import path

from . import views

app_name = "moderation"

urlpatterns = [
    path("report/", views.file_report, name="file_report"),
    path("reports/", views.report_list, name="report_list"),
    path("reports/<int:report_id>/", views.report_detail, name="report_detail"),
    path("jobs/", views.job_moderation_list, name="job_moderation_list"),
    path("jobs/<int:job_id>/deactivate/", views.job_deactivate, name="job_deactivate"),
    path("export/", views.export_csv, name="export_csv"),
]
