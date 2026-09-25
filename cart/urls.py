from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("add/<int:job_id>/", views.add_job, name="add_job"),
    path("remove/<int:job_id>/", views.remove_job, name="remove_job"),
]
