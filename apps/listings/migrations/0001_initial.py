
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SearchHistory",
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
                ("keyword", models.CharField(max_length=255)),
            ],
            options={
                "db_table": "search_history",
            },
        ),
        migrations.CreateModel(
            name="ViewHistory",
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
            ],
            options={
                "db_table": "view_history",
            },
        ),
        migrations.CreateModel(
            name="Address",
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
                (
                    "land",
                    models.CharField(
                        help_text="Федеральная земля (Bundesland)", max_length=100
                    ),
                ),
                ("city", models.CharField(max_length=100)),
                ("street", models.CharField(blank=True, max_length=255)),
                ("postal_code", models.CharField(blank=True, max_length=10)),
            ],
            options={
                "db_table": "addresses",
                "indexes": [
                    models.Index(fields=["city"], name="addresses_city_dfd875_idx"),
                    models.Index(fields=["land"], name="addresses_land_b76f96_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Apartment",
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
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("rooms", models.PositiveSmallIntegerField()),
                (
                    "housing_type",
                    models.CharField(
                        choices=[
                            ("APARTMENT", "Квартира"),
                            ("HOUSE", "Дом"),
                            ("STUDIO", "Студия"),
                            ("ROOM", "Комната"),
                        ],
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="apartments",
                        to="listings.address",
                    ),
                ),
            ],
            options={
                "db_table": "apartments",
                "ordering": ["-created_at"],
            },
        ),
    ]
