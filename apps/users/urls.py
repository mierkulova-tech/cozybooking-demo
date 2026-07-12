
from django.urls import path

from apps.users.controller.auth_controllers import (
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
]
