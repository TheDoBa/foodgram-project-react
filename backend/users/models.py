from django.contrib.auth.models import AbstractUser
from django.db import models

from core.consts import CHAR_FIELD_LENGTH, EMAIL_FIELD_LENGTH
from api.validators import username_validator


class FoodUser(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=EMAIL_FIELD_LENGTH
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=CHAR_FIELD_LENGTH,
        unique=True,
        validators=(username_validator,),
    )
    first_name = models.CharField(
        'Имя',
        max_length=CHAR_FIELD_LENGTH)
    last_name = models.CharField(
        'Фамилия',
        max_length=CHAR_FIELD_LENGTH
    )
    password = models.CharField(
        'Пароль',
        max_length=CHAR_FIELD_LENGTH
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username} - {self.email}'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


class Follow(models.Model):
    """Модель класса Follow."""

    user = models.ForeignKey(
        FoodUser,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    following = models.ForeignKey(
        FoodUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_relationships',
                fields=('user', 'following'),
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            ),
        )

    def __str__(self):
        return (f'{self.user} подписан на {self.following}')
