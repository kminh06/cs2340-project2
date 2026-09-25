from django.urls import path

from . import views

app_name = "searches"

urlpatterns = [
    path("", views.saved_search_list, name="saved_search_list"),
    path("new/", views.saved_search_create, name="saved_search_create"),
    path("notifications/", views.notification_list, name="notification_list"),
]
