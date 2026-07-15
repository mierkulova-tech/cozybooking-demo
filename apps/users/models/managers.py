from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction


class UserManager(BaseUserManager):
    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, email, name, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен.")

        email = self.normalize_email(email)

        user = self.model(email=email, name=name, **extra_fields)

        user.set_password(password)

        user.full_clean(exclude=["password"])

        user.save(using=self._db)

        return user

    def create_user(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        if extra_fields.get("is_active") is not True:
            raise ValueError("Суперпользователь должен иметь is_active=True.")

        return self._create_user(email, name, password, **extra_fields)
