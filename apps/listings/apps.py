from django.apps import AppConfig
from django.db.models import CharField, TextField
from django.db.models.functions import Length


class ListingsConfig(AppConfig):
    name = "apps.listings"

    def ready(self):
        CharField.register_lookup(Length)
        TextField.register_lookup(Length)
