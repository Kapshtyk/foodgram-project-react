import json
import os
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

MODEL_AND_FILE_TABLE = {
    Ingredient: "ingredients.json",
}


class Command(BaseCommand):
    """
    Command to transfer data from csv files to the Django database.

    Performs an additional simple check on startup,
    if such data models exist in the database.
    """

    help = "Import JSON data to DB"

    def handle(self, *args, **options):
        for model, file_name in MODEL_AND_FILE_TABLE.items():
            if model.objects.exists():
                print(
                    f"Data already exists in {model._meta.verbose_name_plural}"
                )
                continue
            file_path = os.path.join(
                settings.BASE_DIR, "..", "data", file_name
            )
            with open(file_path, "r") as file:
                data = json.load(file)
            model.objects.bulk_create(
                [model(**item) for item in data], ignore_conflicts=True
            )
            print(f"Data imported to {model._meta.verbose_name_plural}")
