## Работа с директорией проекта на виртуальной машине:
+ Создать директорию:
```shell script
mkdir foodgram
```

+ Отправить `.env`, `docker-compose.production.yml`, `nginx.conf` из директории `infra` на ваш удаленный сервер используя `SCP`:
```shell script
scp -i <путь к ключам сервера> .env <login@ip>:<путь к директории на сервере>/.env
```
```shell script
scp -i <путь к ключам сервера> docker-compose.production.ym <login@ip>:<путь к директории на сервере>/docker-compose.production.yml
```
```shell script
scp -i <путь к ключам сервера> nginx.conf <login@ip>:<путь к директории на сервере>/nginx.conf
```