from typing import Any
from django.shortcuts import render
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action

from .permissions import AuthorOrReadOnly, ReadOnly
from .models import Ingredient, Recipe, Subscription,Tag
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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnly, ]
    serializer_class = RecipeCreateSerializer


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    # permission_classes = [permissions.AllowAny, ]
    serializer_class = TagSerializer


class SubcriptionsViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
