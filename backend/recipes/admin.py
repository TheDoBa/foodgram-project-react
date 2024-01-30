from django.contrib import admin

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    Favorite,
    ShoppingCart
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )
    list_filter = (
        'name',
        'slug',
    )
    search_fields = ('name', 'color')
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'display_ingredients',
        'display_tags',
        'in_favourite_count',
    )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    ordering = ('name',)

    def in_favourite_count(self, obj):
        """Количество рецептов в избранном."""
        return Favorite.objects.filter(recipe=obj).count()
    in_favourite_count.short_description = 'В избранном'

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, recipe):
        return ', '.join(
            ingredient.name for ingredient in recipe.ingredients.all()
        )

    @admin.display(description='Теги')
    def display_tags(self, recipe):
        return ', '.join(
            tag.name for tag in recipe.tags.all()
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов рецепта."""

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    list_filter = ('recipe',)
    search_fields = ('recipe',)
    ordering = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранных рецептов."""

    list_display = (
        'user',
        'recipe',
    )
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = (
        'user',
        'recipe',
    )
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('user',)
