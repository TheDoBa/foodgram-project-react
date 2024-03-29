# Проект "Foodgram"

Работа над проектом «Фудграм» - сайт для рецептов

Основные возможности:
- публикация рецепта
- добавление рецептов в избранное
- подписки на других авторов
- сервис Список покупок
- реализация админ панели

## Технический стек:
- [Python 3.9.10](https://docs.python.org/release/3.9.10/)
- [Django 3.2](https://docs.djangoproject.com/en/3.2/)
- [Django REST Framework 3.12.4](https://www.django-rest-framework.org/topics/documenting-your-api/)
- [gunicorn 20.1.0](https://pypi.org/project/gunicorn/)
- [python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)

## Запуск проекта:
[файл примера переменных](./infra/.env.example)

[развёртывание проекта](./SetUp.md)

## Примеры запроса в Postman:

### 1 Пример:
```
http://localhost/api/recipes/
```
```
{
  "ingredients": [
    {
      "id": 4380,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

### 2 Пример:

```
http://localhost/api/auth/token/login/
```
```
{
"email": "22221@yandex.ru",
"password": "Qwerty123"
}
```

## Комманда:

[GitHub](https://github.com/yandex-praktikum) | Автор проекта - Yandex Practicum  

[GitHub](https://github.com/TheDoBa) | Разработчик - Vladimir Avizhen
