import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers

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
        return (
            user.is_authenticated
            and following.following.filter(following=following).exists()
        )


class FollowSerializer(serializers.ModelSerializer):
    """Cериализатор подписки."""

    is_subscribed = serializers.ReadOnlyField(
        source='is_following'
    )
    recipes = serializers.ReadOnlyField(
        source='get_following_recipes'
    )
    recipes_count = serializers.ReadOnlyField(
        source='get_following_recipes_count'
    )

    class Meta:
        model = FoodUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if hasattr(user, 'following'):
                return user.following.filter(following=obj).exists()
            else:
                return False
        return False

    def get_recipes(self, obj):
        """Возвращает рецепты автора."""
        recipes = Recipe.objects.filter(author=obj)
        return RecipeReadSerializer(
            recipes,
            many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return obj.recipes.count()

    def validate(self, data):
        """Проверяет наличие подписки на самого себя и повторную подписку."""
        user = self.context['request'].user
        followed_user = self.instance
        if user == followed_user:
            raise serializers.ValidationError(
                "Вы не можете подписаться на себя.")
        if Follow.objects.filter(user=user, following=followed_user).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя.")

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
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount'
        )
    # Пояснение к использованию:
    # amount = serializers.IntegerField(write_only=True):
    # В этом контексте amount представляет собой количество ингредиента в
    # рецепте. Здесь amount указан как write_only, потому что это поле
    # используется только для ввода данных при создании или обновлении
    # рецепта. Мы не хотим включать его в вывод (представление) рецепта.
    # amount предоставляет информацию о количестве данного ингредиента в
    # рецепте, но не нужно возвращать это значение пользователю в виде
    # представления рецепта.

    # Этот сериализатор используется в RecipeWriteSerializer для
    # взаимодействия с ингредиентами в процессе создания и обновления рецепта.
    # При отправке данных для создания (или обновления) рецепта, мы можем
    # указать id ингредиента и его количество amount. Это позволяет управлять
    # связью между рецептом и его ингредиентами, предоставляя удобный способ
    # добавления и управления списком ингредиентов при создании или
    # редактировании рецепта.


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


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели для создания рецепта."""

    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
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
        ingredient_ids = [ingredient_data['id']
                          for ingredient_data in ingredients]
        ingredients_dict = Ingredient.objects.in_bulk(ingredient_ids)

        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            ingredient_instance = ingredients_dict.get(ingredient_id)

            if ingredient_instance:
                recipe_ingredient = RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_instance,
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
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        """Меняет экземпляр в его представление."""
        request = self.context.get('request')
        context = {'request': request}
        serializer = RecipeReadSerializer(instance, context=context)
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели для получени рецепта."""

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
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, recipe):
        """Получает ингредиенты для рецепта."""
        recipe_ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )
        return recipe_ingredients

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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


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
            'id',
            'name',
            'image',
            'cooking_time'
        )
