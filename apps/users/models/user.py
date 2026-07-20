"""Custom user model with email-based authentication and role support."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.common.models.base import BaseModel
from apps.users.choices.role_choices import RoleChoices
from apps.users.models.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Custom user model authenticated by email, with a renter/lessor role."""

    name = models.CharField(max_length=150)

    email = models.EmailField(unique=True, max_length=254)

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.RENTER,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        """Database table name and integrity constraints for User."""

        db_table = "users"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=RoleChoices.values),
                name="user_role_valid",
            ),
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="user_name_not_empty",
            ),
        ]

    def clean(self):
        """Normalize the email address to lowercase before validation."""
        super().clean()
        if self.email:
            self.email = self.email.lower()

    def anonymize(self) -> None:
        """Scrub personally identifiable information for GDPR-compliant deletion.

        Replaces the name and email with placeholder values, disables the
        password, and deactivates the account while preserving the row
        (and its foreign key relations) for referential integrity.
        """
        self.name = "Deleted user"
        self.email = f"deleted-{self.id}@deleted.local"
        self.set_unusable_password()
        self.is_active = False

    def __str__(self):
        """Return a human-readable representation showing email and role."""
        return f"{self.email} ({self.role})"
