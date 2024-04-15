from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    fields = ['name', 'author', 'image', 'tags', 'text',
              'cooking_time', 'favored_counter']
    search_fields = ['name']
    readonly_fields = ('favored_counter',)
    list_display = ['name', 'author']
    list_filter = ['name', 'author', 'tags']


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ['name']
    list_display = ['name', 'measurement_unit']
    search_fields = ['name']


class TagAdmin(admin.ModelAdmin):
    list_filter = ['name', 'slug']
    list_display = ['name', 'color', 'slug']
    search_fields = ['name']


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
admin.site.unregister(Group)
