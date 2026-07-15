from django.db import transaction

from apps.listings.repositories.apartment_repository import ApartmentRepository
from apps.users.errors.users_errors import EmailAlreadyExistsError
from apps.users.models import User
from apps.users.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.apartment_repository = ApartmentRepository()

    def register(self, name: str, email: str, password: str, role: str) -> User:
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
        user.anonymize()
        self.repository.save(user)
        self.apartment_repository.deactivate_by_owner(user.id)
