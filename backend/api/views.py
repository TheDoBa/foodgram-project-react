from rest_framework import viewsets
from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions

from .serializers import (
    FoodUserSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeWriteSerializer,
    RecipeReadSerializer,
)
from core.filters import IngredientFilter
from users.models import FoodUser
from recipes.models import Ingredient, Recipe, Tag


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = FoodUserSerializer
    queryset = FoodUser.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Дает доступ аутентифицированным пользователям."""

        if self.action in ('me',):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ('get',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeWriteSerializer
    queryset = Recipe.objects.all()
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer
