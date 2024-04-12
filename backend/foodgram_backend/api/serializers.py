from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .fields import Base64ImageField


User = get_user_model()


class UserSubscribedMixin:
    def check_subscription(self, author):
        user_id = self.context.get('user_id')
        if not bool(user_id):
            return False
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return False
        return user.subscriptions.filter(pk=author.pk).exists()


class UserSerializer(serializers.ModelSerializer, UserSubscribedMixin):
    is_subscribed = serializers.SerializerMethodField(
        method_name='check_subscription')

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
        )


class RecipesMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserWithRecipesSerializer(serializers.ModelSerializer,
                                UserSubscribedMixin):
    is_subscribed = serializers.SerializerMethodField(
        method_name='check_subscription')
    recipes_count = serializers.SerializerMethodField(
        method_name='count_recipes')
    recipes = RecipesMinifiedSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count'
                  )

    def count_recipes(self, obj):
        return obj.recipes.count()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


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
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='check_in_shopping_cart', required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'ingredients', 'image', 'name', 'text',
                  'cooking_time', 'tags', 'author', 'is_favorited',
                  'is_in_shopping_cart']
        depth = 1

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            ingredient['recipe'] = recipe
        ingredients = [IngredientInRecipe(**data) for data in ingredients_data]
        print(ingredients)
        IngredientInRecipe.objects.bulk_create(ingredients)
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
                IngredientInRecipe.objects.create(**new_ingredient,
                                                  recipe=recipe)
        for ingredient in old_ingredients_list:
            ingredient.delete()
        return recipe

    def to_internal_value(self, data):
        print(data['ingredients'])
        for ingredient in data['ingredients']:
            ingredient['ingredient'] = ingredient.pop('id')
        print(data['ingredients'])
        result = super().to_internal_value(data)
        return result

    def check_favorites(self, obj):
        user_id = self.context['request'].user.id
        if not bool(user_id):
            return False
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return False
        return obj in user.favorite_recipes.all()

    def check_in_shopping_cart(self, obj):
        user_id = self.context['request'].user.id
        if not bool(user_id):
            return False
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return False
        return obj in user.shopping_cart.all()
