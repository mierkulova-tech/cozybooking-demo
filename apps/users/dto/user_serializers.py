"""User authentication and profile serializers.

This module provides serializers for user registration and user response representation
within the cozybooking project, utilizing Django REST Framework.
"""

from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.users.choices.role_choices import RoleChoices
from apps.users.models import User


class RegisterSerializer(serializers.Serializer):
    """Serializer for handling new user registration data validation.

    Validates user input fields including name, email, password strength, and role.
    """

    name = serializers.CharField(max_length=150)

    email = serializers.EmailField()

    password = serializers.CharField(min_length=8, write_only=True)

    role = serializers.ChoiceField(choices=RoleChoices.choices)

    def validate_password(self, value):
        """Validate the password against Django's built-in security validators.

        Args:
            value (str): The raw password string to validate.

        Returns:
            str: The validated password string.

        Raises:
            serializers.ValidationError: If the password fails any security requirements.
        """
        try:
            django_validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

        return value


class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for serializing User model instances into response data."""

    class Meta:
        """Meta options for UserResponseSerializer."""

        model = User

        fields = ["id", "name", "email", "role"]
