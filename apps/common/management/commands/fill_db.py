import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from apps.listings.models.apartment import Apartment
from apps.listings.models.address import Address
from apps.reservations.models.reservation import Reservation
from apps.reviews.models.review import Review

from apps.listings.choices.housing_choices import HousingTypeChoices
from apps.users.choices.role_choices import RoleChoices
from apps.reservations.choices.status_choices import StatusChoices

User = get_user_model()


class Command(BaseCommand):
    help = "Полное наполнение базы CozyBooking (Пользователи, Квартиры, Бронирования, Отзывы)"

    def handle(self, *args, **kwargs):
        fake = Faker(["en_US", "de_DE"])

        self.stdout.write("=== Начинаю полное наполнение базы данных CozyBooking ===")

        users = []
        available_roles = [RoleChoices.RENTER, RoleChoices.LESSOR]

        for _ in range(12):
            email = fake.unique.email()
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    name=fake.name(),
                    password="password123",
                    role=random.choice(available_roles),
                    is_active=True,
                )
                users.append(user)
            else:
                users.append(User.objects.get(email=email))

        lessors = [u for u in users if u.role == RoleChoices.LESSOR]
        renters = [u for u in users if u.role == RoleChoices.RENTER]

        if not lessors:
            lessors = users[:4]
        if not renters:
            renters = users[4:]

        self.stdout.write(f"Успешно обработано пользователей: {len(users)}")

        apartments = []
        housing_types = [
            HousingTypeChoices.APARTMENT,
            HousingTypeChoices.HOUSE,
            HousingTypeChoices.STUDIO,
            HousingTypeChoices.ROOM,
        ]

        fake_de = fake["de_DE"]
        for _ in range(15):
            address = Address.objects.create(
                land=fake_de.state(),
                city=fake_de.city(),
                street=fake_de.street_address(),
                postal_code=fake_de.postcode(),
            )

            apartment_titles = [
                f"Cozy {random.choice(['Apartment', 'Flat'])} in {address.city}",
                f"Beautiful {random.choice(['House', 'Studio'])} centrally located",
                f"Modern room in {address.city} near Central Station",
                f"Bright and spacious apartment in {address.city}",
            ]

            apt = Apartment.objects.create(
                owner=random.choice(lessors),
                address=address,
                title=random.choice(apartment_titles),
                description=fake["en_US"].text(max_nb_chars=400),
                price=random.randint(500, 2800),
                rooms=random.randint(1, 5),
                housing_type=random.choice(housing_types),
                is_active=True,
            )
            apartments.append(apt)

        self.stdout.write(f"Успешно создано объявлений: {len(apartments)}")

        self.stdout.write("Генерирую бронирования и отзывы...")

        today = timezone.now().date()
        statuses = [
            StatusChoices.PENDING,
            StatusChoices.CONFIRMED,
            StatusChoices.CANCELED,
        ]

        for apt in apartments:
            for i in range(random.randint(1, 2)):
                renter = random.choice(renters)

                if i == 0:
                    start_date = today - timedelta(days=random.randint(40, 90))
                    end_date = start_date + timedelta(days=random.randint(30, 60))

                    res = Reservation.objects.create(
                        listing=apt,
                        user=renter,
                        start_date=start_date,
                        end_date=end_date,
                        status=StatusChoices.CHECKED_IN,
                    )

                    Review.objects.create(
                        listing=apt,
                        user=renter,
                        reservation=res,
                        rating=random.randint(4, 5),
                        comment=fake["en_US"].paragraph(nb_sentences=2),
                    )
                else:
                    start_date = today + timedelta(days=random.randint(5, 30))
                    end_date = start_date + timedelta(days=random.randint(30, 90))

                    Reservation.objects.create(
                        listing=apt,
                        user=renter,
                        start_date=start_date,
                        end_date=end_date,
                        status=random.choice(statuses),
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "=== Успех! База данных CozyBooking полностью готова к работе! ==="
            )
        )
