import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe

from users.models import Follow, FoodUser


class UserSerializer(serializers.ModelSerializer):
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
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создает нового пользователя."""
        return FoodUser.objects.create_user(**validated_data)

    def get_is_subscribed(self, following):
        """Проверяет подписку на автора."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=following).exists()


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
            'id',
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


class Base64ImageField(serializers.ImageField):
    """Сериализатор для загрузки изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта."""

    author = UserSerializer(read_only=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
        )
        read_only_fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
        )
