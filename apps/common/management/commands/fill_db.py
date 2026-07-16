import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.listings.choices.housing_choices import HousingTypeChoices
from apps.listings.models.address import Address
from apps.listings.models.apartment import Apartment
from apps.reservations.choices.status_choices import StatusChoices
from apps.reservations.models.reservation import Reservation
from apps.users.choices.role_choices import RoleChoices

User = get_user_model()


class Command(BaseCommand):
    help = "Наполнение базы CozyBooking демонстрационными данными"

    def handle(self, *args, **kwargs):
        fake = Faker(["en_US", "de_DE"])

        self.stdout.write("=== Начинаю наполнение базы данных CozyBooking ===")
        if Apartment.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Демо-данные уже есть в базе — пропускаю наполнение."
                )
            )
            return

        users = self._create_users(fake)
        lessors = [user for user in users if user.role == RoleChoices.LESSOR]
        renters = [user for user in users if user.role == RoleChoices.RENTER]

        apartments = self._create_apartments(fake, lessors)

        self._create_reservations(apartments, renters)

        self.stdout.write(
            self.style.SUCCESS("=== База данных CozyBooking готова к работе ===")
        )

    def _create_users(self, fake):
        users = []

        for index in range(6):
            email = f"renter{index + 1}@example.com"

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": fake.name(),
                    "role": RoleChoices.RENTER,
                    "is_active": True,
                },
            )

            user.set_password("password123")
            user.save()

            users.append(user)

        for index in range(6):
            email = f"lessor{index + 1}@example.com"

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": fake.name(),
                    "role": RoleChoices.LESSOR,
                    "is_active": True,
                },
            )

            user.set_password("password123")
            user.save()

            users.append(user)

        self.stdout.write(f"Обработано пользователей: {len(users)}")

        return users

    def _create_apartments(self, fake, lessors):
        apartments = []

        housing_types = [
            HousingTypeChoices.APARTMENT,
            HousingTypeChoices.HOUSE,
            HousingTypeChoices.STUDIO,
            HousingTypeChoices.ROOM,
        ]

        fake_de = fake["de_DE"]

        for index in range(15):
            address = Address.objects.create(
                land=fake_de.state(),
                city=fake_de.city(),
                street=fake_de.street_address(),
                postal_code=fake_de.postcode(),
            )

            title = f"Cozy apartment {index + 1} in {address.city}"

            apartment = Apartment.objects.create(
                owner=random.choice(lessors),
                address=address,
                title=title,
                description=fake["en_US"].text(max_nb_chars=400),
                price=random.randint(500, 2800),
                rooms=random.randint(1, 5),
                housing_type=random.choice(housing_types),
                is_active=True,
            )

            apartments.append(apartment)

        self.stdout.write(f"Создано объявлений: {len(apartments)}")

        return apartments

    def _create_reservations(self, apartments, renters):
        today = timezone.now().date()

        statuses = [
            StatusChoices.PENDING,
            StatusChoices.CONFIRMED,
            StatusChoices.CANCELED,
        ]

        reservations_count = 0

        for apartment in apartments:
            start_date = today + timedelta(days=random.randint(5, 30))

            end_date = start_date + timedelta(days=random.randint(5, 20))

            nights = (end_date - start_date).days

            total_price = apartment.price * nights

            Reservation.objects.create(
                listing=apartment,
                user=random.choice(renters),
                start_date=start_date,
                end_date=end_date,
                status=random.choice(statuses),
                price=total_price,
            )

            reservations_count += 1

        self.stdout.write(f"Создано бронирований: {reservations_count}")
