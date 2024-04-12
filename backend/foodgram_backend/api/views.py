from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import Ingredient, Recipe, Tag
from .filters import IngredientsSearchFilter
from .permissions import AuthorOrReadOnly, PasswordPermission
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer,
                          UserWithRecipesSerializer)

User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination
    token_generator = default_token_generator
    lookup_field = 'pk'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.AllowAny(),)
        if self.action == 'destroy':
            return (permissions.IsAdminUser(),)
        if self.action == 'set_password':
            return (permissions.IsAuthenticated(), PasswordPermission(),)
        if self.action in ('retrieve', 'subscriptions'):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=kwargs['pk'])
        if user == author:
            content = {'error': 'нельзя подписываться на себя'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            if user.subscriptions.filter(pk=author.pk).exists():
                content = {'error': 'вы уже подписаны на этого автора'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            user.subscriptions.add(author)
            return Response(self.retrieve(request, *args, **kwargs).data,
                            status=status.HTTP_201_CREATED)
        try:
            if not user.subscriptions.filter(pk=author.pk).exists():
                content = {'error': 'подписка не найдена'}
                return Response(content,
                                status=status.HTTP_400_BAD_REQUEST)
            user.subscriptions.remove(author)
        except Exception:
            return Response(content,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['GET'])
    def me(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.id
        return self.retrieve(self, request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def set_password(self, request, *args, **kwargs):
        user = request.user
        user.set_password(request.data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'subscriptions':
            serializer = UserWithRecipesSerializer(
                self.get_queryset(),
                context={'user_id': self.request.user.id},
                many=True)
            return serializer
        if self.action == 'subscribe':
            serializer = UserWithRecipesSerializer(
                self.get_object(),
                context={'user_id': self.request.user.id},
                many=False
            )
            return serializer
        if self.action == 'create':
            serializer = UserCreateSerializer(*args, **kwargs)
            return serializer
        return UserSerializer(
            *args,
            **kwargs,
            context={'user_id': self.request.user.id}
        )

    def get_queryset(self):
        if self.action == 'subscriptions':
            return self.request.user.subscriptions.all()
        return User.objects.all()


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [permissions.AllowAny, ]
    http_method_names = ['get', ]
    serializer_class = IngredientSerializer
    filter_backends = [IngredientsSearchFilter]
    search_fields = ['^name', ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnly, ]
    serializer_class = RecipeCreateSerializer
    filterset_fields = ['author']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(favored_by=self.request.user)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(shopping_carts=self.request.user)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def get_permissions(self):
        if self.action in ('favorite', 'shopping_cart'):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        if request.method == 'POST':
            if user.favorite_recipes.filter(pk=recipe.pk).exists():
                content = {'error': 'этот рецепт уже в избранных'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            user.favorite_recipes.add(recipe)
            return Response(self.retrieve(request, *args, **kwargs).data,
                            status=status.HTTP_201_CREATED)
        if not user.favorite_recipes.filter(pk=recipe.pk).exists():
            content = {
                'error': 'в вашем избранном не найден указанный рецепт'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        user.favorite_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        if request.method == 'POST':
            user.shopping_cart.add(recipe)
            return Response(
                self.retrieve(request, *args, **kwargs).data,
                status=status.HTTP_201_CREATED
            )
        user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        shopping_list = {}
        for recipe in user.shopping_cart.all():
            for ingredient in recipe.ingredients.all():
                if ingredient.ingredient.name in shopping_list:
                    shopping_list[ingredient.ingredient.name]['total']\
                        += ingredient.amount
                else:
                    shopping_list[ingredient.ingredient.name]\
                        = {'total': ingredient.amount}
                    shopping_list[ingredient.ingredient.name]['measure']\
                        = ingredient.ingredient.measurement_unit
                    shopping_list[ingredient.ingredient.name]['recipes']\
                        = []
                shopping_list[ingredient.ingredient.name]['recipes'].\
                    append([recipe.name, ingredient.amount])
        content = ''
        for ingredient, details in shopping_list.items():
            content += f'• {ingredient}:'
            content += '.' * (80 - len(
                ingredient + str(details["total"])
                + details["measure"]))
            content += f'{details["total"]} {details["measure"]}.\n'
            for recipe in details['recipes']:
                content += f'\t({recipe[0]}: {recipe[1]})\n'

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.\
            format('shopping_cart.txt')
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
