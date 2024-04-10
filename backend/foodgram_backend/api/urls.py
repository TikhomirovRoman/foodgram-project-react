from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, IngredientViewset, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewset, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
