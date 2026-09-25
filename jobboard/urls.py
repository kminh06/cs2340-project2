"""
URL configuration for the jobboard project.

Each app owns a clear URL prefix; see STORIES.md for which app/urls/views
implement which user story.
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('jobs/', include('jobs.urls')),
    path('applications/', include('applications.urls')),
    path('cart/', include('cart.urls')),
    path('messages/', include('messaging.urls')),
    path('searches/', include('searches.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('maps/', include('maps.urls')),
    path('moderation/', include('moderation.urls')),
]
