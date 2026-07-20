"""URL routing configuration for the users application.

This module defines URL patterns for user authentication, registration,
token refresh, and account management endpoints.
"""

from django.urls import path

from apps.users.controller.auth_controllers import (
    DeleteAccountController,
    LoginController,
    LogoutController,
    RefreshController,
    RegisterController,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterController.as_view(), name="register"),
    path("login/", LoginController.as_view(), name="login"),
    path("logout/", LogoutController.as_view(), name="logout"),
    path("token/refresh/", RefreshController.as_view(), name="token-refresh"),
    path("me/", DeleteAccountController.as_view(), name="delete-account"),
]
