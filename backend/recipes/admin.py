from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = (
        'id',
        'name',
        'color',
        'slug'
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
        'display_tags'
    )
    search_fields = ('name',)
    ordering = ('name',)

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        return ', '.join(
            ingredient.name for ingredient in obj.ingredients.all()
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        return ', '.join(
            tag.name for tag in obj.tags.all()
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов рецепта."""

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe',)
    ordering = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранных рецептов."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    ordering = ('user',)
