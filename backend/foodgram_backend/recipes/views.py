from django.shortcuts import render
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import permissions

from .models import Ingredient
from .serializers import IngredientSerializer

class IngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'

class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [permissions.AllowAny,]
    http_method_names = ['get',]
    serializer_class = IngredientSerializer
    filter_backends = [IngredientsSearchFilter]
    search_fields = ['^name',]
