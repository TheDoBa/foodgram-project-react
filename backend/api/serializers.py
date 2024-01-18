from rest_framework import serializers

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
