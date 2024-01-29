## Развёртывание проекта на виртуальной машине:
+ Включить и залогиниться в 'Docker'
```shell script
docker login
```

+ Создать образы контейнеров `Backend`, `Frontend` из главной директории в локальном проекте 

```shell script
cd foodgram-project-react/
```

```shell script
docker build -t <your-docker-username>/foodgram_backend backend/
```

```shell script
docker push <your-docker-username>/foodgram_backend
```

```shell script
docker build -t <your-docker-username>/foodgram_frontend frontend/
```

```shell script
docker push <your-docker-username>/foodgram_frontend
```
### контейнеры DB и nginx будут созданы автоматически

[настройка сервера](./SetUpServSettings.md)
[подготовка директории проекта](./SetUpServDip.md)

## Запуск проекта на сервере:

+ Перейти в директорию:
```shell script
cd foodgram/
```
Запуск проекта на сервере:
+ Запустить `Docker` контейнеры:
```shell script
scp -i sudo docker compose -f docker-compose.production.yml up -d
```
+ Настройки `Backend`:
```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

```shell script
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
```

```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

+ Загрузить список ингредиентов в бд:
```shell script
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_csv
```

+ Проверить, что контейнеры работают:
```shell script
scp -i sudo docker compose -f docker-compose.production.yml ps
```
## Доступ к api/docs по:
https://yaprak.ddns.net/api/docs/

### Данные для входа:
Если уж зашёл подсмотреть то не надо хулиганить с постами. Не порти карму.
```
#Superuser
admin@ad.by
1234

#User1
kol@av.by
1234

#User2
1234
```