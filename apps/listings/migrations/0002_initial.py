import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("listings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="apartment",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="apartments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="searchhistory",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="searches",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="viewhistory",
            name="apartment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="views",
                to="listings.apartment",
            ),
        ),
        migrations.AddField(
            model_name="viewhistory",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="viewed_apartments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(fields=["price"], name="apartments_price_d71607_idx"),
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(fields=["rooms"], name="apartments_rooms_4d49e0_idx"),
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(
                fields=["housing_type"], name="apartments_housing_0123af_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="apartment",
            index=models.Index(
                fields=["is_active"], name="apartments_is_acti_e2dc23_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="searchhistory",
            index=models.Index(
                fields=["keyword"], name="search_hist_keyword_03b4bf_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="viewhistory",
            index=models.Index(
                fields=["apartment"], name="view_histor_apartme_b0545b_idx"
            ),
        ),
    ]
