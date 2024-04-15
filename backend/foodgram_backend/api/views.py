from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .filters import IngredientsSearchFilter
from .pagination import CustomPagination
from .permissions import (StaffOrAuthorOrReadOnly, PasswordPermission)
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipesMinifiedSerializer, RecipeSerializer,
                          TagSerializer, UserCreateSerializer, UserSerializer,
                          UserWithRecipesSerializer)

User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
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
        if self.action == 'me':
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
            kwargs.setdefault('context', {'request': request})
            return Response(self.retrieve(request, *args, **kwargs).data,
                            status=status.HTTP_201_CREATED)
        try:
            if not user.subscriptions.filter(pk=author.pk).exists():
                content = {'error': 'подписка не найдена'}
                return Response(content,
                                status=status.HTTP_400_BAD_REQUEST)
            user.subscriptions.remove(author)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def me(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.id
        return self.retrieve(self, request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def set_password(self, request, *args, **kwargs):
        try:
            user = request.user
            user.set_password(request.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'subscriptions':
            serializer = UserWithRecipesSerializer(
                self.get_queryset(),
                context={'request': self.request},
                many=True)
            return serializer
        if self.action == 'subscribe':
            serializer = UserWithRecipesSerializer(
                self.get_object(),
                context={'request': self.request},
                many=False
            )
            return serializer
        if self.action == 'create':
            serializer = UserCreateSerializer(*args, **kwargs)
            return serializer
        kwargs.setdefault('context', {'request': self.request})
        return UserSerializer(*args, **kwargs)

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
    pagination_class = CustomPagination
    permission_classes = [StaffOrAuthorOrReadOnly, ]
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
        kwargs.setdefault('context', self.get_serializer_context())
        if self.action in ('favorite', 'shopping_cart'):
            return RecipesMinifiedSerializer(*args, **kwargs)
        if self.action in ('retrieve', 'list'):
            return RecipeSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def add_romove_related(self, request, related_models,
                           related_name, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        if request.method == 'POST':
            if related_models.filter(pk=recipe.pk).exists():
                content = {
                    'error':
                    f"этот рецепт уже добавлен в '{related_name}' ранее"}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            related_models.add(recipe)
            return Response(
                self.retrieve(request, *args, **kwargs).data,
                status=status.HTTP_201_CREATED
            )
        if not related_models.filter(pk=recipe.pk).exists():
            content = {
                'error': f"указанный рецепт не найден в '{related_name}'"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        related_models.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        response = self.add_romove_related(
            request,
            related_models=request.user.favorite_recipes,
            related_name='избранное',
            *args,
            **kwargs)
        return response

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        response = self.add_romove_related(
            request,
            related_models=request.user.shopping_cart,
            related_name='список покупок',
            *args,
            **kwargs)
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        total = IngredientInRecipe.objects\
            .filter(recipe__in=user.shopping_cart.all())\
            .values('ingredient', 'ingredient__name',
                    'ingredient__measurement_unit')\
            .annotate(total=Sum('amount'))
        content = ''
        for item in total.all():
            content += f'• {item["ingredient__name"]}'
            content += f'({item["ingredient__measurement_unit"]}):'
            content += ('.' * (80 - len(
                item["ingredient__name"] + item["ingredient__measurement_unit"]
                + str(item['total']))))
            content += f'{item["total"]}\n'

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.\
            format('shopping_cart.txt')
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
