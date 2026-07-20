"""Repository module for handling User database operations.

This module provides data access encapsulation for the User model,
handling operations such as checking existence, retrieval by email,
creation, and persistence.
"""

from apps.users.models import User


class UserRepository:
    """Repository class encapsulating database queries and mutations for User instances."""

    def exists_by_email(self, email: str) -> bool:
        """Check whether a user with the specified email already exists in the database.

        Args:
            email (str): The email address to check.

        Returns:
            bool: True if a user with this email exists, False otherwise.
        """
        return User.objects.filter(email=email).exists()

    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user instance by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The matching User instance if found, otherwise None.
        """
        return User.objects.filter(email=email).first()

    def create(self, name: str, email: str, password: str, role: str) -> User:
        """Create and persist a new user instance using the user manager.

        Args:
            name (str): The display name of the user.
            email (str): The unique email address of the user.
            password (str): The raw password to be hashed.
            role (str): The assigned role for the user.

        Returns:
            User: The newly created User instance.
        """
        return User.objects.create_user(
            name=name,
            email=email,
            password=password,
            role=role,
        )

    def save(self, user: User) -> User:
        """Save changes made to an existing User instance to the database.

        Args:
            user (User): The User instance to save.

        Returns:
            User: The updated User instance.
        """
        user.save()
        return user
