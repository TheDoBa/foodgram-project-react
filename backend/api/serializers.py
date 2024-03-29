import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    ShoppingCart,
    Tag,
    Recipe,
    RecipeIngredient,
)
from users.models import Follow

FoodUser = get_user_model()


class FoodUserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создает нового пользователя."""
        return FoodUser.objects.create_user(**validated_data)

    def get_is_subscribed(self, following):
        """Проверяет подписку на автора."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return following.following.filter(user=user).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта из избранного."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    email = serializers.ReadOnlyField(source='following.email')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = Follow
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and Follow.objects.filter(
            user=request.user,
            following=obj.following
        ).exists()

    def get_recipes(self, obj):
        """Возвращает рецепты автора."""
        recipes = obj.following.recipes.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')

        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]

        return RecipeReadSerializer(
            recipes,
            many=True,
            context={'request': self.context.get('request')}).data


class FollowSubSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        """Проверяет наличие подписки на самого себя и повторную подписку."""
        request = self.context.get('request')
        user = request.user

        # Проверка на подписку на самого себя
        if user == data['following']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.')

        # Проверка на повторную подписку
        existing_subscription = Follow.objects.filter(
            user=user, following=data['following'])
        if existing_subscription.exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.')

        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        read_only_fields = (
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        read_only_fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиента и количества в рецепт."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class Base64ImageField(serializers.ImageField):
    """Сериализатор для загрузки изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name='temp.{}'.format(ext)
            )

        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели для создания рецепта."""

    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """Создает список ингредиентов."""
        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            amount = abs(ingredient_data['amount'])
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_id,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Меняет экземпляр в его представление."""
        request = self.context.get('request')
        context = {'request': request}
        serializer = RecipeReadSerializer(instance, context=context)
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели для получения рецепта."""

    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = FoodUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, recipe):
        """Получает ингредиенты для рецепта."""
        recipe_ingredients = recipe.recipeingredient_set.all()
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверяет есть ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет есть ли рецепт в списке покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe=obj
        ).exists()
