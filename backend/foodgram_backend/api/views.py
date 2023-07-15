from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


User = get_user_model()

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # permission_classes = (IsAdminOrSuper,)
    pagination_class = LimitOffsetPagination
    token_generator = default_token_generator
    lookup_field = 'username'
    # filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(["GET", "PATCH"], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.kwargs['username'] = request.user.username
        if request.method == 'GET':

            return self.retrieve(request, *args, **kwargs)
        elif request.method == 'PATCH':
            if (request.data.get('role', request.user.role)
                    != request.user.role):
                return Response('changing \'role\' isn\'t allowed',
                                status=status.HTTP_403_FORBIDDEN)
            return self.partial_update(request, *args, **kwargs)
