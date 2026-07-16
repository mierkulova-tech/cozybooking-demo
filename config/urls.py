from django.http import JsonResponse
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def home(request):
    return JsonResponse(
        {
            "message": "Добро пожаловать в CozyBooking API!",
            "docs": "/api/docs/",
            "admin": "/admin/",
        }
    )


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
