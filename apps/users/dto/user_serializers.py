
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.users.choices.role_choices import RoleChoices

from apps.users.models import User


class RegisterSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=150)

    email = serializers.EmailField()

    password = serializers.CharField(min_length=8, write_only=True)

    role = serializers.ChoiceField(choices=RoleChoices.choices)

    def validate_password(self, value):

        try:
            django_validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

        return value


class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = ["id", "name", "email", "role"]
