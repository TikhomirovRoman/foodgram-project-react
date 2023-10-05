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
from djoser import utils,views
from djoser.conf import settings
from recipes.models import Subscription


User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
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
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, *args, **kwargs):
        User = get_user_model()
        follower = request.user
        following = get_object_or_404(User, pk=kwargs['pk'])
        if follower == following:
            content = {'error': 'нельзя подписываться на себя. стыдно'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            try:
                Subscription.objects.create(follower=follower,
                                            following=following)
            except IntegrityError:
                content = {'error': 'вы уже подписаны на этого автора'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'subscribed!!!'},
                            status=status.HTTP_201_CREATED)
        else:
            try:
                subscription = Subscription.objects.filter(follower=follower,
                                                           following=following).first()
                if not subscription:
                    content = {'error': 'подписка не найдена'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                subscription.delete()
            except Exception as e:
                print(e)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=None, methods=['GET']):
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = user.subscriptions

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)