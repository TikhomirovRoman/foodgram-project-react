from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Recipe
from django.core.exceptions import ObjectDoesNotExist
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
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
       

    def check_subscription(self, obj):
        user_id = self.context.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return False
        return obj in user.subscriptions.all()

class RecipesMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

class UserWithRecipesSerializer(serializers.ModelSerializer):
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

    def check_subscription(self, obj):
        user_id = self.context.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return False
        return obj in user.subscriptions.all()

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
