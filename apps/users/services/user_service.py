
from apps.users.errors.users_errors import EmailAlreadyExistsError

from apps.users.models import User

from apps.users.repositories.user_repository import UserRepository


class UserService:

    def __init__(self):

        self.repository = UserRepository()

    def register(self, name: str, email: str, password: str, role: str) -> User:

        if self.repository.exists_by_email(email):
            raise EmailAlreadyExistsError()

        return self.repository.create(
            name=name,
            email=email,
            password=password,
            role=role,
        )
