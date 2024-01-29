## Развёртывание проекта:
+ Клонировать репозиторий и перейти в него в командной строке:
```shell script
git clone git@github.com:TheDoBa/foodgram-project-react.git
```

```shell script
cd foodgram-project-react/backend/
```
+ Cоздать и активировать виртуальное окружение (Windows/Bash):
```shell script
python -m venv venv
```

```shell script
source venv/Scripts/activate
```

+ Установить зависимости из файла requirements.txt:
```shell script
python -m pip install --upgrade pip
```

```shell script
pip install -r backend/requirements.txt
```

+ Установите [Docker compose](https://www.docker.com/) на свой компьютер.

+ Запустите проект через docker-compose:
```shell script
docker compose -f docker-compose.production.yml up --build -d
```

+ Выполнить миграции:
```shell script
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

+ Соберите статику:
```shell script
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

+ Скопируйте статику:
```shell script
docker compose -f docker-compose.production.yml exec backend cp -r /app/static_backend/. /backend_static/static/
```

+ Создать файл `.env` с переменными окружениями:

[Примеры переменных окружения](./.env.example)

```shell script
docker compose -f docker-compose.production.yml up --build -d
```

+ Выполнить миграции:
```shell script
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

+ Собрать статику:
```shell script
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

```shell script
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
```

[развертка проекта локально](./SetUpLocal.md)
[развертка проекта на сервере](./SetUpServ.md)