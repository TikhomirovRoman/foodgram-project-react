import csv
from os.path import dirname, join, normcase
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient

CSV_FILE = join(
    dirname(dirname(settings.BASE_DIR)),
    normcase('data/ingredients.csv')
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'measurement_unit']
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            for row in reader:
                try:
                    ingredient = Ingredient(**row)
                    ingredient.save()
                except IntegrityError as e:
                    print(e)
