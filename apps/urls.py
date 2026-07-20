"""Main application URL routing configuration for cozybooking project.

The `urlpatterns` list routes URLs to app-specific URL modules. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import include, path

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("listings/", include("apps.listings.urls")),
    path("reservations/", include("apps.reservations.urls")),
    path("reviews/", include("apps.reviews.urls")),
]
