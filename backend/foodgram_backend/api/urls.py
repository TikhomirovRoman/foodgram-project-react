from django.urls import path, include
from rest_framework import routers
# from rest_framework.authtoken import views
from .views import UserViewSet, CustomTokenCreateView #, CustomAuthToken
from recipes.views import IngredientViewset



router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('ingredients', IngredientViewset, basename='ingredients')

urlpatterns = [
    path('auth/token/login/', CustomTokenCreateView.as_view(), name="login"),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
