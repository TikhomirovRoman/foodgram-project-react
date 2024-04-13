from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from api.validators import validate_hex_color

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient_measure')]
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Tag (models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='название')
    color = models.CharField(
        max_length=7,
        validators=[validate_hex_color],
        verbose_name='цвет')
    slug = models.SlugField(
        max_length=200,
        verbose_name='ссылка')

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='название')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='иллюстрация')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги')
    text = models.TextField(verbose_name='текст')
    cooking_time = models.PositiveIntegerField(
        verbose_name='время приготовления')

    @property
    def favored_counter(self):
        return self.favored_by.count()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        related_name='recipes',
        verbose_name='ингредиент')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='количество')

    class Meta:
        verbose_name = 'ингредиент-рецепт'
        verbose_name_plural = 'ингредиенты-рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')
        ]
