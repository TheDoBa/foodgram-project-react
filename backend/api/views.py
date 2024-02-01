import io
from django.db.models import Sum
from django_filters import rest_framework as filters
from django.http import FileResponse
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
from recipes.models import (
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    RecipeIngredient
)
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
        """Метод для подписки и отписки от авторов."""
        author = get_object_or_404(FoodUser, id=id)
        user = request.user
        if request.method == 'POST':
            Follow.objects.get_or_create(user=user, following=author)
            serializer = FollowSubSerializer(
                instance=Follow(user=user, following=author),
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user.following.filter(following=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


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
        if serializer.is_valid():
            if request.method == 'POST':
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif request.method == 'DELETE':
                recipe.favorite_set.filter(user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if request.method == 'POST' and serializer.is_valid():
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredient_totals = (
            RecipeIngredient.objects
            .filter(recipe__shoppingcart__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(amount=Sum('amount'))
        )

        content = 'Список ингредиентов для покупок:\n'
        for ingredient in ingredient_totals:
            content += (
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) '
                f'- {ingredient["amount"]}\n'
            )

        # Преобразуем строку в байты
        content_bytes = content.encode('utf-8')

        response = FileResponse(
            io.BytesIO(content_bytes),
            as_attachment=True,
            filename="ShoppingList.txt",
            content_type='text/plain'
        )

        return response