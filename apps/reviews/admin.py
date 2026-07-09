from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "user", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["listing__title", "comment"]
