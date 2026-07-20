"""Custom manager for creating regular and superuser accounts."""

from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction


class UserManager(BaseUserManager):
    """Manager that handles user creation with validation and password hashing."""

    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, email, name, password, **extra_fields):
        """Create, validate, and persist a user with the given credentials.

        Args:
            email: The user's email address (used as the login field).
            name: The user's display name.
            password: Raw password to be hashed before saving.
            **extra_fields: Additional model fields (e.g. is_staff, is_superuser).

        Returns:
            The newly created and saved User instance.

        Raises:
            ValueError: If no email is provided.
            django.core.exceptions.ValidationError: If full_clean() fails.
        """
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)

        user = self.model(email=email, name=name, **extra_fields)

        user.set_password(password)

        user.full_clean(exclude=["password"])

        user.save(using=self._db)

        return user

    def create_user(self, email, name, password=None, **extra_fields):
        """Create a regular (non-staff, non-superuser) user account.

        Args:
            email: The user's email address.
            name: The user's display name.
            password: Raw password to be hashed. May be None.
            **extra_fields: Additional model fields.

        Returns:
            The newly created User instance.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, email, name, password=None, **extra_fields):
        """Create a superuser account with full permissions.

        Args:
            email: The user's email address.
            name: The user's display name.
            password: Raw password to be hashed. May be None.
            **extra_fields: Additional model fields.

        Returns:
            The newly created superuser instance.

        Raises:
            ValueError: If is_staff, is_superuser, or is_active are not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")

        return self._create_user(email, name, password, **extra_fields)
