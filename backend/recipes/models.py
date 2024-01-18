from django.db import models
from core.validators import color_validator, slug_validator
from users.models import FoodUser

from core.consts import (
    CHAR_FIELD_LENGTH,
    CHAR_FIELD_LENGTH_COLOR,
    CHAR_FIELD_LENGTH_MIDDLE,
    CHAR_FIELD_LENGTH_MAX
)


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=CHAR_FIELD_LENGTH_MAX,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингридиента',
        max_length=CHAR_FIELD_LENGTH_MAX
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=CHAR_FIELD_LENGTH
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=CHAR_FIELD_LENGTH_COLOR,
        validators=[color_validator],
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True,
        validators=[slug_validator],
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',)
    name = models.CharField(
        'Название рецепта',
        max_length=CHAR_FIELD_LENGTH_MIDDLE)
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='static/recipes/',
        blank=True,
        null=True)
    text = models.TextField(
        'Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',)
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента')

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        FoodUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',)

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        FoodUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',)

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'
