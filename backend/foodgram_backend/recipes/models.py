from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_hex_color

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'measurement_unit']


class Tag (models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, validators=[validate_hex_color])
    slug = models.SlugField(max_length=200)

    def __str__(self):
        return self.name



class Recipe(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    image = models.ImageField(upload_to='recipes/images/',
                              null=True,
                              default=None)
    tags = models.ManyToManyField(Tag, related_name='recipes')
    text = models.TextField()
    cooking_time = models.IntegerField()
    @property
    def favored_counter(self):
        return self.favored_by.count()

    def __str__(self) -> str:
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.RESTRICT,
                                   related_name='recipes')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
