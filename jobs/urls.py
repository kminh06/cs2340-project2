from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_search, name="job_search"),
    path("mine/", views.job_list_mine, name="job_list_mine"),
    path("new/", views.job_create, name="job_create"),
    path("<int:pk>/", views.job_detail, name="job_detail"),
    path("<int:pk>/edit/", views.job_edit, name="job_edit"),
]
