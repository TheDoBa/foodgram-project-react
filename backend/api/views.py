import csv
import io
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, FloatField, Count
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions
from rest_framework.decorators import action

from .serializers import (
    FavoriteSerializer,
    FavoriteRecipeSerializer,
    FoodUserSerializer,
    FollowSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeWriteSerializer,
    RecipeReadSerializer,
)
from core.filters import IngredientFilter
from users.models import Follow, FoodUser
from recipes.models import Ingredient, Recipe, ShoppingCart, Tag, RecipeIngredient


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = FoodUserSerializer
    queryset = FoodUser.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Дает доступ аутентифицированным пользователям."""
        if self.action in ('me', 'subscribe', 'subscriptions'):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Возвращает подписки."""
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        """Метод для подписки и отписки."""
        user = self.request.user
        following = self.get_object()
        if request.method == 'POST':
            Follow.objects.create(user=user, following=following)
            serializer = FollowSerializer(
                following, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Follow.objects.filter(user=user, following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Метод для добавления и удаления рецепта в избранное."""
        recipe = self.get_object()
        user = request.user
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        if request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shoping_cart(self, request, pk=None):
        """Метод для добавления и удаления рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={
                'request': request,
                'action_name': 'shoping_cart'
            }
        )
        if request.method == 'POST':
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',))
    def download_shopping_cart(self, request):
        """Отдает пользователю список для покупок в виде TXT файла."""
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user).select_related(
            'recipe__ingredients'
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit',
            'recipe__recipe_ingredients__amount'
        )
        ingredient_totals = {}

        for item in shopping_cart:
            key = (
                f'{item["recipe__ingredients__name"]} '
                f'({item["recipe__ingredients__measurement_unit"]})'
            )
            if key in ingredient_totals:
                ingredient_totals[key] += item["recipe__recipe_ingredients__amount"]
            else:
                ingredient_totals[key] = item["recipe__recipe_ingredients__amount"]

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="ShoppingList.txt"'

        with io.StringIO() as buffer:
            buffer.write('Список ингредиентов для покупки:\n')
            for ingredient, amount in ingredient_totals.items():
                buffer.write(f'{ingredient} - {amount}\n')

            response.write(buffer.getvalue())

        return response