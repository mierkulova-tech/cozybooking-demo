
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.common.models.base import BaseModel
from apps.users.choices.role_choices import RoleChoices
from apps.users.models.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

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
        db_table = "users"

        constraints = [
            models.CheckConstraint(
                check=models.Q(role__in=RoleChoices.values),
                name="user_role_valid",
            ),
            models.CheckConstraint(
                check=~models.Q(name=""),
                name="user_name_not_empty",
            ),
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"


