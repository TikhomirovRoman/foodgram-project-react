from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(max_length=120)
    measurement_unit = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'measurement_unit']