
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0003_alter_address_postal_code_alter_apartment_price_and_more"),
        ("reservations", "0004_reservation_price_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(
                fields=["listing", "start_date", "end_date"],
                name="reservation_listing_fb7304_idx",
            ),
        ),
    ]
