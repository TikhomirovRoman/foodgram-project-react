from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .fields import Base64ImageField


User = get_user_model()


class UserSubscribedMixin:
    def check_subscription(self, author):
        user_id = self.context['request'].user.id
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


class UserWithRecipesSerializer(serializers.ModelSerializer,
                                UserSubscribedMixin):
    is_subscribed = serializers.SerializerMethodField(
        method_name='check_subscription')
    recipes_count = serializers.SerializerMethodField(
        method_name='count_recipes')
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )

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

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit', None)
        if recipes_limit:
            recipes_limit = int(recipes_limit)
        queryset = obj.recipes.all()[:recipes_limit]
        return RecipesMinifiedSerializer(
            queryset, many=True, read_only=True).data


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


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
        required=True,
        read_only=False
    )
    name = serializers.CharField(
        source='ingredient.name',
        required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True,
                                               read_only=False,
                                               required=True)
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True,
                         read_only=True)
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

    def check_favorites(self, obj):
        user_id = self.context['request'].user.id
        if not bool(user_id):
            return False
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return False
        return user.favorite_recipes.filter(pk=obj.pk).exists()

    def check_in_shopping_cart(self, obj):
        user_id = self.context['request'].user.id
        if not bool(user_id):
            return False
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return False
        return user.shopping_cart.filter(pk=obj.pk).exists()


class RecipeCreateSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Tag.objects.all()
    )

    def save_recipe(self, validated_data, instance=None):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if instance:
            recipe = super().update(instance, validated_data)
            recipe.ingredients.all().delete()
        else:
            recipe = Recipe.objects.create(**validated_data)

        ingredients = [IngredientInRecipe(**data, recipe=recipe)
                       for data in ingredients_data]
        IngredientInRecipe.objects.bulk_create(ingredients)
        recipe.tags.set(tags)
        return recipe

    def create(self, validated_data):
        return self.save_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.save_recipe(validated_data,
                                instance)
