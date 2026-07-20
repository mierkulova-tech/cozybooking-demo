"""API views for registration, login/logout, token refresh, and account deletion."""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.dto.token_serializers import CustomTokenObtainPairSerializer
from apps.users.dto.user_serializers import RegisterSerializer, UserResponseSerializer
from apps.users.services.user_service import UserService


class _RefreshInputSerializer(serializers.Serializer):
    """Input schema for endpoints that accept a raw refresh token."""

    refresh = serializers.CharField()


class RegisterController(APIView):
    """Register a new user account."""

    permission_classes = [AllowAny]
    throttle_scope = "auth"

    @extend_schema(
        tags=["Users"],
        summary="Register a user",
        description="Creates a new user (renter or lessor).",
        request=RegisterSerializer,
        responses={
            201: UserResponseSerializer,
            400: OpenApiResponse(
                description="Validation error (email already exists, weak password, etc.)"
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """Validate registration input and create the new user account."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        user = service.register(
            name=serializer.validated_data["name"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            role=serializer.validated_data["role"],
        )
        response_serializer = UserResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Users"],
    summary="Log in",
    description="Authenticates the user and returns a JWT pair (access + refresh).",
    responses={200: CustomTokenObtainPairSerializer},
)
class LoginController(TokenObtainPairView):
    """Authenticate a user and issue a JWT access/refresh token pair."""

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "auth"


class LogoutController(APIView):
    """Log out the current user by blacklisting their refresh token."""

    permission_classes = [IsAuthenticated]
    throttle_scope = "auth"

    @extend_schema(
        tags=["Users"],
        summary="Log out",
        description="Invalidates the refresh token via the blacklist.",
        request=_RefreshInputSerializer,
        responses={
            205: OpenApiResponse(description="Logged out successfully"),
            400: OpenApiResponse(
                description="A refresh token is required, or the token is invalid"
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """Blacklist the provided refresh token to end the user's session."""
        refresh = request.data.get("refresh")

        if not refresh:
            return Response(
                {
                    "error": {
                        "code": "refresh_required",
                        "detail": "A refresh token is required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {
                    "error": {
                        "code": "invalid_token",
                        "detail": "The token is invalid or has already been blacklisted.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_205_RESET_CONTENT)


@extend_schema(
    tags=["Users"],
    summary="Refresh access token",
    description="Obtain a new access token using a valid refresh token.",
)
class RefreshController(TokenRefreshView):
    """Issue a new access token from a valid refresh token."""

    throttle_scope = "auth"


class DeleteAccountController(APIView):
    """Delete (anonymize and deactivate) the requesting user's account."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        summary="Delete account",
        description="Anonymizes the user's data and deactivates the account.",
        responses={204: OpenApiResponse(description="Account successfully deleted (anonymized)")},
    )
    def delete(self, request, *args, **kwargs):
        """Anonymize and deactivate the requesting user's account."""
        service = UserService()
        service.delete_account(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
