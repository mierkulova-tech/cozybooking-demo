import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Ожидает подтверждения"),
                            ("CONFIRMED", "Подтверждено"),
                            ("REJECTED", "Отклонено"),
                            ("CHECKED_IN", "Заселение состоялось"),
                            ("CANCELED", "Отменено"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="listings.apartment",
                    ),
                ),
            ],
            options={
                "db_table": "reservations",
                "ordering": ["-created_at"],
            },
        ),
    ]
