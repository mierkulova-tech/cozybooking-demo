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
    refresh = serializers.CharField()


class RegisterController(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    @extend_schema(
        tags=["Users"],
        summary="Регистрация пользователя",
        description="Создает нового пользователя (арендатора или арендодателя).",
        request=RegisterSerializer,
        responses={
            201: UserResponseSerializer,
            400: OpenApiResponse(
                description="Ошибка валидации (email уже существует, слабый пароль и т.д.)"
            ),
        },
    )
    def post(self, request, *args, **kwargs):
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
    summary="Вход в систему (Login)",
    description="Аутентификация пользователя и получение пары JWT токенов (access + refresh).",
    responses={200: CustomTokenObtainPairSerializer},
)
class LoginController(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "auth"


class LogoutController(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "auth"

    @extend_schema(
        tags=["Users"],
        summary="Выход из системы (Logout)",
        description="Погашает refresh token через blacklist.",
        request=_RefreshInputSerializer,
        responses={
            205: OpenApiResponse(description="Успешный выход"),
            400: OpenApiResponse(
                description="Нужен refresh token или токен недействителен"
            ),
        },
    )
    def post(self, request, *args, **kwargs):
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


@extend_schema(
    tags=["Users"],
    summary="Обновление access токена",
    description="Получение нового access token по валидному refresh token.",
)
class RefreshController(TokenRefreshView):
    throttle_scope = "auth"


class DeleteAccountController(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        summary="Удаление аккаунта",
        description="Анонимизирует данные пользователя и деактивирует аккаунт.",
        responses={
            204: OpenApiResponse(description="Аккаунт успешно удалён (анонимизирован)")
        },
    )
    def delete(self, request, *args, **kwargs):
        service = UserService()
        service.delete_account(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
