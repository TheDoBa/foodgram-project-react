Установить `Docker` на сервер:
```shell script
sudo apt update
```

```shell script
sudo apt --fix-broken install
```

```shell script
sudo apt install curl
```

```shell script
curl -fSL https://get.docker.com -o get-docker.sh
```

```shell script
sudo sh ./get-docker.sh
```

```shell script
sudo apt-get install docker-compose-plugin
```

Настроить `Nginx` на сервере:
```shell script
sudo apt install nginx -y
```

```shell script
sudo systemctl start nginx
```

```shell script
sudo nano /etc/nginx/sites-enabled/default
```

+ Добавить конфигурации:
```
server {
    server_name <your-ip> <your-domen>;
    server_tokens off;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
}
```
```shell script
sudo nginx -t
```

```shell script
sudo service nginx reload
```

+ Проверить работоспособность:
```shell script
sudo systemctl status nginx
```

Получить `SSl` сертификат:
+ Настраить `Firewall`:
```shell script
sudo ufw allow 'Nginx Full'
```

```shell script
sudo ufw allow OpenSSH
```

```shell script
sudo ufw enable
```

+ Установить `Certbot`:
```shell script
sudo apt install snapd 
```

```shell script
sudo snap install core; sudo snap refresh core
```

```shell script
sudo snap install --classic certbot
```

```shell script
sudo ln -s /snap/bin/certbot /usr/bin/certbot 
```

```shell script
sudo certbot --nginx 
```

+ Автопродление сертификата:
```shell script
sudo certbot certificates
```

```shell script
sudo certbot renew --dry-run 
```

```shell script
sudo certbot renew --pre-hook "service nginx stop" --post-hook "service nginx start" 
```