
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0003_alter_address_postal_code_alter_apartment_price_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="apartment",
            name="views_count",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(
                fields=["views_count"], name="apartments_views_c_02e804_idx"
            ),
        ),
    ]
