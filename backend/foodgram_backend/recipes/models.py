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


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='recipes/images/',
                              null=True,
                              default=None)
    tags = models.ManyToManyField(Tag)
    text = models.TextField()
    cooking_time = models.IntegerField()


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.RESTRICT,
                                   related_name='recipes')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])


class Subscription(models.Model):
    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='subscriptions')
    following = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='subscribers')
    class Meta:
        unique_together = ('follower', 'following',)
