# Развертка проекта локально:

переходим в дерикторию infra-dev
```shell script
cd infra-dev/
```
+ Запускаем проект через docker-compose:
```shell script
docker compose -f docker-compose.yml up --build -d
```
+ Выполнить миграции:
```shell script
docker compose -f docker-compose.yml exec backend python manage.py migrate
```
+ Соберите статику:
```shell script
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
## Важно:
Нужно принять следующие настройки в .env
```
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django

DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=secret_key
DEBUG=False
ALLOWED_HOSTS=000.000.00.00,000.0.0.0,localhost,your_host.com
```
[пример nginx](./infra-dev/nginx.conf)

<br>

### Так же требуется перенастройка url путей. 