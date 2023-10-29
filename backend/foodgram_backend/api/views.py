from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from djoser.views import UserViewSet
from djoser.conf import settings
from api.serializers import UserWithRecipesSerializer, UserCreateSerializer


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination
    token_generator = default_token_generator
    lookup_field = 'pk'
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.AllowAny(),)
        if self.action == 'destroy':
            print('permissions DESTROY')
            return (permissions.IsAdminUser(),)
        if self.action in ('retrieve', 'subscriptions'):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, *args, **kwargs):
        User = get_user_model()
        user = request.user
        author = get_object_or_404(User, pk=kwargs['pk'])
        if user == author:
            content = {'error': 'нельзя подписываться на себя. стыдно'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            if author in user.subscriptions.all():
                content = {'error': 'вы уже подписаны на этого автора'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            user.subscriptions.add(author)
            return Response(self.retrieve(request, *args, **kwargs).data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                if author not in user.subscriptions.all():
                    content = {'error': 'подписка не найдена'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                user.subscriptions.remove(author)
            except Exception as e:
                print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['GET'])
    def me(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.id
        return self.retrieve(self, request, *args, **kwargs)

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
        else:
            return UserSerializer(
                *args,
                **kwargs,
                context={'user_id': self.request.user.id}
                )

    def get_queryset(self):
        if self.action == 'subscriptions':
            queryset = self.request.user.subscriptions.all()
            return queryset
        return User.objects.all()
