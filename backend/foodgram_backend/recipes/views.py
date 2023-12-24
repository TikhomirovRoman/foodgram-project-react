from typing import Any
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
import json

from .permissions import AuthorOrReadOnly, ReadOnly
from .models import Ingredient, Recipe, Tag
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    TagSerializer
)


class IngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'


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
        queryset =  super().get_queryset()
        print(self.request.query_params)
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(favored_by = self.request.user)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(shopping_carts = self.request.user)

        tags = self.request.query_params.getlist('tags')
        print("TAGS: ", tags)
        print("QUERYSET BEFORE FILTER: ", queryset)
        print()
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        print("QUERYSET AFTER FILTER: ", queryset)
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
            if recipe in user.favorite_recipes.all():
                content = {'error': 'этот рецепт уже в избранных'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            user.favorite_recipes.add(recipe)
            return Response(self.retrieve(request, *args, **kwargs).data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if recipe not in user.favorite_recipes.all():
                content = {'error': 'в вашем избранном не найден указанный рецепт'}
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
        elif request.method == 'DELETE':
            user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        shopping_list = {}
        for recipe in user.shopping_cart.all():
            for ingredient in recipe.ingredients.all():
                old_amount = shopping_list.get(ingredient.ingredient.name, 0)
                shopping_list[ingredient.ingredient.name] = old_amount + ingredient.amount
        content = json.dumps(shopping_list, ensure_ascii=False)
        response =  HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format('filename.txt')
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
