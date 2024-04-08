from django.contrib import admin
from .models import Ingredient, Recipe, Tag, IngredientInRecipe
from django.contrib.auth.models import Group


class RecipeAdmin(admin.ModelAdmin):
    fields = ['name', 'author', 'image', 'tags', 'text',
              'cooking_time', 'favored_counter']
    search_fields = ['name']
    readonly_fields = ('favored_counter',)
    list_display = ['name', 'author']
    list_filter = ['name', 'author', 'tags']


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ['name']
    search_fields = ['name']


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
admin.site.unregister(Group)
