
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0003_alter_address_postal_code_alter_apartment_price_and_more"),
        ("reservations", "0003_reservation_reservation_end_after_start_and_more"),
        ("reviews", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="review",
            constraint=models.CheckConstraint(
                condition=models.Q(("rating__gte", 1), ("rating__lte", 5)),
                name="review_rating_range",
            ),
        ),
    ]
