from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions

from api.serializers import UserSerializer
from users.models import FoodUser


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = UserSerializer
    queryset = FoodUser.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Дает доступ аутентифицированным пользователям."""

        if self.action in ('me',):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)