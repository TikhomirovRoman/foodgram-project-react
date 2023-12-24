from rest_framework import serializers
from .models import Ingredient, IngredientInRecipe, Recipe, Tag
from api.serializers import UserSerializer

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import base64
from django.core.files.base import ContentFile
User = get_user_model()

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    def to_internal_value(self, data):
        return Tag.objects.get(pk=data)


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



class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        depth = 1


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True,
                                               read_only=False,
                                               required=True)
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=False)
    author = UserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='check_favorites', required=False)
    class Meta:
        model = Recipe
        fields = ['id', 'ingredients', 'image', 'name', 'text', 'cooking_time', 'tags', 'author', 'is_favorited']
        depth = 1

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
        result = super().to_internal_value(data)
        return result

    def check_favorites(self, obj):
        user_id = self.context['request'].user.id
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return False
        return obj in user.favorite_recipes.all()

class RecipesMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
