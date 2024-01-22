from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, FoodUser


@admin.register(FoodUser)
class FoodUserAdmin(BaseUserAdmin):
    """Админка пользователей."""

    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )
    search_fields = ('username', 'first_name')
    ordering = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ('following', 'user')
    search_fields = ('following',)
