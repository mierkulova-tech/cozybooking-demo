import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="postal_code",
            field=models.CharField(
                blank=True,
                max_length=10,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Некорректный почтовый индекс.", regex="^\\d{4,10}$"
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="apartment",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[
                    django.core.validators.MinValueValidator(
                        0.01, message="Цена должна быть больше нуля."
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="apartment",
            name="rooms",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, message="Должна быть минимум 1 комната."
                    ),
                    django.core.validators.MaxValueValidator(
                        5,
                        message="Слишком много комнат — проверьте значение, максимум 5.",
                    ),
                ]
            ),
        ),
        migrations.AddConstraint(
            model_name="address",
            constraint=models.CheckConstraint(
                condition=models.Q(("city", ""), _negated=True),
                name="address_city_not_empty",
            ),
        ),
        migrations.AddConstraint(
            model_name="address",
            constraint=models.CheckConstraint(
                condition=models.Q(("land", ""), _negated=True),
                name="address_land_not_empty",
            ),
        ),
        migrations.AddConstraint(
            model_name="apartment",
            constraint=models.CheckConstraint(
                condition=models.Q(("price__gt", 0)), name="apartment_price_positive"
            ),
        ),
        migrations.AddConstraint(
            model_name="apartment",
            constraint=models.CheckConstraint(
                condition=models.Q(("rooms__gte", 1), ("rooms__lte", 5)),
                name="apartment_rooms_reasonable",
            ),
        ),
        migrations.AddConstraint(
            model_name="apartment",
            constraint=models.CheckConstraint(
                condition=models.Q(("title__length__gte", 5)),
                name="apartment_title_min_length",
            ),
        ),
        migrations.AddConstraint(
            model_name="apartment",
            constraint=models.CheckConstraint(
                condition=models.Q(("description__length__gte", 20)),
                name="apartment_description_min_length",
            ),
        ),
        migrations.AddConstraint(
            model_name="apartment",
            constraint=models.CheckConstraint(
                condition=models.Q(("housing_type__in", ["APARTMENT", "HOUSE", "STUDIO", "ROOM"])),
                name="apartment_housing_type_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="searchhistory",
            constraint=models.CheckConstraint(
                condition=models.Q(("keyword", ""), _negated=True),
                name="search_history_keyword_not_empty",
            ),
        ),
    ]
