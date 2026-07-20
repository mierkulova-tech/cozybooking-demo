"""Business logic for user registration, authentication support, and account deletion."""

from django.db import transaction

from apps.listings.repositories.apartment_repository import ApartmentRepository
from apps.users.errors.users_errors import EmailAlreadyExistsError
from apps.users.models import User
from apps.users.repositories.user_repository import UserRepository


class UserService:
    """Service layer for managing user business logic, registration, and account lifecycle."""

    def __init__(self):
        """Initialize the user service with required user and apartment repositories."""
        self.repository = UserRepository()
        self.apartment_repository = ApartmentRepository()

    def register(self, name: str, email: str, password: str, role: str) -> User:
        """Register and persist a new user account with duplicate email validation.

        Args:
            name: The display name of the user.
            email: The unique email address used for user authentication.
            password: The raw password to be securely hashed and saved.
            role: The designated role assigned to the user (e.g., RENTER or LESSOR).

        Returns:
            User: The newly created and saved User model instance.

        Raises:
            EmailAlreadyExistsError: If a user with the specified email already exists.
        """
        if self.repository.exists_by_email(email):
            raise EmailAlreadyExistsError()

        return self.repository.create(
            name=name,
            email=email,
            password=password,
            role=role,
        )

    @transaction.atomic
    def delete_account(self, user: User) -> None:
        """Safely anonymize a user account and deactivate all associated properties.

        Executes within an atomic database transaction to ensure data integrity
        across both user anonymization and listing deactivation.

        Args:
            user (User): The user instance targeted for account deletion.
        """
        user.anonymize()
        self.repository.save(user)
        self.apartment_repository.deactivate_by_owner(user.id)
