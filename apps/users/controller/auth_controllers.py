
from rest_framework import serializers, status

from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.dto.user_serializers import RegisterSerializer, UserResponseSerializer

from apps.users.services.user_service import UserService

from apps.users.dto.token_serializers import CustomTokenObtainPairSerializer


class _RefreshInputSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterController(APIView):

    permission_classes = [AllowAny]

    throttle_scope = "auth"

    def post(self, request):

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


class LoginController(TokenObtainPairView):

    permission_classes = [AllowAny]

    serializer_class = CustomTokenObtainPairSerializer

    throttle_scope = "auth"


class LogoutController(APIView):

    permission_classes = [IsAuthenticated]

    throttle_scope = "auth"

    def post(self, request):

        refresh = request.data.get("refresh")

        if not refresh:
            return Response(
                {
                    "error": {
                        "code": "refresh_required",
                        "detail": "Нужен refresh-токен.",
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
                        "detail": "Токен недействителен или уже погашен.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_205_RESET_CONTENT)


class RefreshController(TokenRefreshView):

    throttle_scope = "auth"
