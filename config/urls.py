"""URL configuration for cozybooking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/

Examples:
    Function views
    1. Greeting/Home view: def home(request): ...
    2. Add an URL to urlpatterns:  path('', home, name='home')
"""

from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def home(request):
    """Render the main landing page view.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered index.html template.
    """
    return render(request, "index.html")


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/<str:version>/", include("apps.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
