from rest_framework import serializers
from .models import Ingredient, IngredientInRecipe, Recipe, Tag
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id']

    def to_internal_value(self, data):
        return {'author': get_user_model().objects.get(pk=data)}

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'email': instance.email,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name
        }


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount,
            }

    class Meta:
        model = IngredientInRecipe
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    ingredients = IngredientInRecipeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recipe
        fields = '__all__'
        depth = 0


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    ingredients = IngredientInRecipeSerializer(many=True,
                                               read_only=False,
                                               required=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        depth: 0

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_item in ingredients_data:
            IngredientInRecipe.objects.create(**ingredient_item, recipe=recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        new_ingredients = validated_data.pop('ingredients')
        new_tags = validated_data.pop('tags')
        author = validated_data.pop('author')
        recipe = super().update(instance, validated_data)
        recipe.tags.set(new_tags)
        old_ingredients_list = [i for i in recipe.ingredients.all()]
        for new_ingredient in new_ingredients:
            ingredient_in_recipe = recipe.ingredients.filter(
                ingredient=new_ingredient['ingredient']).first()
            if ingredient_in_recipe:
                old_ingredients_list.remove(ingredient_in_recipe)
                if new_ingredient['amount'] != ingredient_in_recipe.amount:
                    ingredient_in_recipe.amount = new_ingredient['amount']
                    ingredient_in_recipe.save()
            else:
                IngredientInRecipe.objects.create(**new_ingredient, recipe=recipe)
        for ingredient in old_ingredients_list:
            ingredient.delete()
        return recipe

    def to_internal_value(self, data):
        for ingredient in data['ingredients']:
            ingredient['ingredient'] = ingredient.pop('id')
        return super().to_internal_value(data)
