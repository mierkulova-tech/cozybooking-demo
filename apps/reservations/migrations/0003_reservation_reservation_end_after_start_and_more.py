
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0003_alter_address_postal_code_alter_apartment_price_and_more"),
        ("reservations", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="reservation",
            constraint=models.CheckConstraint(
                condition=models.Q(("end_date__gt", models.F("start_date"))),
                name="reservation_end_after_start",
            ),
        ),
        migrations.AddConstraint(
            model_name="reservation",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "status__in",
                        ["PENDING", "CONFIRMED", "REJECTED", "CHECKED_IN", "CANCELED"],
                    )
                ),
                name="reservation_status_valid",
            ),
        ),
    ]
