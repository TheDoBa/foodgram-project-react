import io
from django.db.models import Sum, F
from django_filters import rest_framework as filters
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import (
    FavoriteRecipeSerializer,
    FoodUserSerializer,
    FollowSerializer,
    FollowSubSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeWriteSerializer,
    RecipeReadSerializer,
)
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, FoodUser


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = FoodUserSerializer
    queryset = FoodUser.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        if self.action in ('me', 'subscriptions', 'subscribe'):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)

    @action(detail=False, methods=('get',))
    def subscriptions(self, request):
        """Возвращает подписки."""
        user = self.request.user
        following = FoodUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None):
        """Метод для подписки и отписки."""
        user = self.request.user
        following = self.get_object()
        if request.method == 'POST':
            Follow.objects.create(user=user, following=following)
            serializer = FollowSubSerializer(
                following, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Follow.objects.filter(user=user, following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ('get',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeWriteSerializer
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'ingredients').all()
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer
    
    def get_permissions(self):
        """Распределение прав на действия."""
        if self.action in (
            'favorite',
            'shopping_cart',
            'download_shopping_cart',
        ):
            return (permissions.IsAuthenticated(),)
        return (IsAuthorOrReadOnly(),)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Метод для добавления и удаления рецепта в избранное."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        if request.method == 'POST':
            if serializer.is_valid():
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        if request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Метод для добавления и удаления рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={
                'request': request,
                'action_name': 'shopping_cart'
            }
        )
        if request.method == 'POST':
            if serializer.is_valid():
                ShoppingCart.objects.create(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user

        ingredient_totals = (
            ShoppingCart.objects
            .filter(user=user)
            .select_related('recipe__ingredients')
            .values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit'
            )
            .annotate(amount=Sum('recipe__recipe_ingredients__amount'))
        )

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="ShoppingList.txt"'

        with io.StringIO() as buffer:
            buffer.write('Список ингредиентов для покупок:\n')
            for ingredient in ingredient_totals:
                buffer.write(
                    f"{ingredient['recipe__ingredients__name']} "
                    f"({ingredient['recipe__ingredients__measurement_unit']}) "
                    f"- {ingredient['amount']}\n"
                )

            response.write(buffer.getvalue())

        return response
