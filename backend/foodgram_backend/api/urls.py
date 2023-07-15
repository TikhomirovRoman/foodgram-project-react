from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet


router = routers.DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
   # path('auth/signup/', signup),
   # path('auth/token/', token),
    path('users', include(router.urls)),
]
