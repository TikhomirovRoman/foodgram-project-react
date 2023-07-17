import os
import csv
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from users.models import User
from django.shortcuts import get_object_or_404


def read_csv(name):
    reader = csv.DictReader(open(
        os.path.join(os.path.dirname(settings.BASE_DIR), '/data/', name),
        'r', encoding='utf-8'), delimiter=',')
    return reader


class Command(BaseCommand):
    def handle(self, *args, **options):

        # # Category Data input
        # for row in read_csv('ingredients.csv'):
        #     sys.stdout.write(str(row))
        #     category = Category(
        #         id=row['id'],
        #         name=row['name'],
        #         slug=row['slug']
        #     )
        #     category.save()

        for row in read_csv:
            _, created = Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1],
                )
