from apps.users.models import User


class UserRepository:
    def exists_by_email(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()

    def get_by_email(self, email: str) -> User | None:
        return User.objects.filter(email=email).first()

    def create(self, name: str, email: str, password: str, role: str) -> User:
        return User.objects.create_user(
            name=name,
            email=email,
            password=password,
            role=role,
        )
