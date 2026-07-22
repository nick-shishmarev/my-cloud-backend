# Дипломный проект по профессии «Fullstack-разработчик на Python»

## 1. Описание бэкенда проекта

Сервер содержит реализацию бэкенда для двух основных блоков 
приложения: административный интерфейс и работа с файловым 
хранилищем.

### 1. Структура базы данных

#### _User_ - кастомная модель на базе _AbstractUser_

Все поля стандартные плюс добавлены полное имя пользователя и путь к 
личному хранилищу.

В проекте используются:
- _id_ - ID пользователя, формируется автоматически
- _username_ - логин пользователя (4-20 символов), 
вводится при регистрации
- _password_ - хешированный пароль пользователя, 
вводится при регистрации, затем хешируется средствами _django_
- _is_staff_ - признак наличия прав администратора
- _email_ - e-mail пользователя, вводится при регистрации
- _fullname_ - полное имя пользователя, вводится при регистрации
- _directory_ - имя личной папки пользователя, формируется 
автоматически при регистрации в виде случайного набора 12
шестнадцатиричных цифр.

Значение поля _is_staff_ любого пользователя может быть изменено 
администратором

#### File - таблица, хранящая сведения о загруженных файлах
- _id_ - ID файла, формируется автоматически
- _original_name_ - имя файла на компьютере пользователя
- _display_name_ - отображаемое в приложении имя файла, вводится 
при загрузке файла пользователем или приравнивается 
к _original_name_
- _size_bytes_ - размер файла в байтах
- _created_at_ - дата загрузки
- _downloaded_at_ - дата последней выгрузки файла
- _comment_ - комментарий, вводится пользователем при загрузке
- _public_url_ - ссылка для прямого доступа к файлу извне, 
формируется автоматически

Значение полей _display_name_ и _comment_ может быть изменено 
владельцем хранилища или администратором

### 2. Эндпойнты:

#### Авторизация и регистрация:
- POST api/register/ - регистрация пользователя — с валидацией входных 
данных на соответствие требованиям, описанным выше;
- POST api/api-token-auth/ - авторизация пользователя по логину и паролю.

#### Файловое хранилище:
- GET api/files/ - получение списка файлов пользователя;
- POST api/files/ - загрузка файла в хранилище;
- DELETE api/files/id - удаление файла из хранилища;
- PATCH api/files/id - переименование файла и/или 
изменение комментария к файлу;
- GET api/files/id/download - скачивание файла по ID;

#### Административная часть
- GET api/users/ - получение списка пользователей;
- GET api/users/id - получение пользователя ао его ID;
- GET api/users/id/files - получение списка файлов, принадлежащих
пользователю с указанным ID;
- DELETE api/users/id - удаление пользователя;

### 3. Аутентификация и авторизация

Аутентификация производиться по логину и паролю пользователя, создаваемыми в 
процессе регистрации по методу токен-аутентификации (Token Authentication).

После аутентификации пользователь получает права в соответствии с полем is_staff. 
Обычный пользователь (is_staff=False) может управлять только своим хранилищем. 
Пользователь-администратор (is_staff=True) может управлять хранилищами любого пользователя 
(кроме загрузки файлов в чужое хранилище), а также удалять других пользователей и
предоставлють любому пользователю права администратора или лишать их. В целях
избежания появления в хранилище "бесхозных" файлов, администратор не может 
удалить пользователя пока у того остается хотя бы один файл.

## 2. Развёртывание приложения

Для развёртывания приложения на сервере Ubuntu необходимо следующее:

### 2.1 Установка и запуск Django-DRF API

- На сервере создать пользователя (в дальнейшем USER), от имени которого будет работать django
- На сервере установить git, postgreSQL, python3.14+, python-pip, python-venv, npm
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git postgresql python3 python3-pip python3-venv npm 
```
- Зайти на сервер под именем _USER_
- В postgreSQL создать пользователя _USER_ с правами суперпользователя для управления 
базой данных django-приложения и базу данных _USER_
```
sudo su postgres
psql
postgres=# create user USER with superuser;
postgres=# alter user USER with password 'USER_PASSWORD';
postgres=# create database USER;
postgres-# \q
exit
```
- В postgreSQL создать базу данных django-приложения _DB_NAME_ от имени _USER_
```
psql
<user>=# create database DB_NAME;
<user>=# \q
```
- Склонировать в домашнюю папку django-приложение из репозитория и перейти в склонированную папку
```
git clone https://github.com/nick-shishmarev/my-cloud-frontend.git
cd my-cloud-frontend
```
- Создать и активировать виртуальное окружение
```
python3 -m venv <venv_name>
source <venv_name>.bin.activate 
```
- Установить зависимости в соответствии с _requirements.txt_.
```
sudo apt update
sudo apt install -y libpq-dev python3-dev build-essential
pip3 install -r requirements.txt
```
- Создать файл _.env_, указав в нем необходимые параметры:
```
SECRET_KEY=ваш секретный ключ
DEBUG=False
DATABASE_URL=postgres://USER:USER_PASSWORD@locaLhost:5432/DB_NAME
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```
- Провести миграцию
```
python3 manage.py makemigrations
python3 manage.py migrate
```
- Создать суперпользователя _django_, он и будет первым администратором приложения
```
python3 manage.py createsuperuser
```
- Создать папку _logs_ для логов _django_
```
mkdir logs
```
- Установить _gunicorn_
```
pip install gunicorn
```
- Создать файл _/etc/systemd/system/gunicorn.service_
```
[Unit]
Description=gunicorn daemon for Django
After=network.target

[Service]
User=USER
Group=www-data
WorkingDirectory=/home/cetus/my-cloud-backend
ExecStart=/home/cetus/my-cloud-backend/venv/bin/gunicorn \
    --access-logfile - \
    --error-logfile - \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    diplom.wsgi:application

[Install]
WantedBy=multi-user.target
```
- Запустить _Django-DRF API_
```
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```
### 2.2 Установить статические файлы фронтенда
- Склонировать в домашнюю папку исходники проекта фронтенда (React)
```
cd ~
git clone https://github.com/nick-shishmarev/my-cloud-frontend.git

```
- Перейти в папку фронтенда, установить зависимости и собрать проект
```
cd my-cloud-frontend/
npm ci
npm run build
```
- Отредактировать файл _config.json_
```
nano dist/config.json
```
Содержимое файла config.json:
```
{
  "BASE_URL": "",
  "BASE_URL_MEDIA": "http://195.19.12.27"
}
```
- Переместить папку dist в папку _/var/www с переименованием в my_cloud_frontend_
```
cd ..
sudo rm -rf /var/www/my_cloud_frontend/
sudo mv ./my-cloud-frontend/dist /var/www/my_cloud_frontend

```
- После перемещения _dist_ папку _my-cloud-frontend_ можно удалить
```
rm -rf my-cloud-frontend/
```
### 2.3 Установить и настроить Nginx
- Установить _Nginx_
```
sudo apt update
sudo apt install nginx

```
- Создать файл _/etc/nginx/sites-available/diplom_
```
sudo nano /etc/nginx/sites-available/diplom
```
с содержимым:
```
server {
     listen 80;
     server_name <ip-адрес или домен сервера>;
     
     # Максимальный размер загружаемых файлов
     client_max_body_size 10M;

     root /var/www/my_cloud_frontend;
     index index.html;

     # API (Django через Gunicorn)
     location /api/ {
         proxy_pass http://127.0.0.1:8000;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;

        # таймауты для долгих запросов
         proxy_read_timeout 300s;
         proxy_connect_timeout 75s;
     }

    # Медиафайлы 
    location /media/ {
        alias /home/cetus/my-cloud-backend/media/;
    }

    # Статика React (собранный проект: build/dist)
     location / {
     #    root /var/www/my-cloud-react-frontend;
     #    root /home/cetus/my-cloud-frontend/dist;
         try_files $uri $uri/ /index.html;
     }

     # location = /favicon.ico {
     #     log_not_found off;
     #     access_log off;
     # }

    # Логи
     access_log /var/log/nginx/my_cloud_access.log;
     error_log  /var/log/nginx/my_cloud_error.log warn;
}
```
- Создать симлинк
```
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/
```
- Проверить конфигурацию _Nginx_
```
sudo nginx -t      # проверка синтаксиса
```
если проверка прошла, перегрузить _Nginx_
```
sudo systemctl reload nginx
```
После развёртывания сервер работает по адресу _ip-адрес или домен сервера_, 
указанному в файле _/etc/nginx/sites-available/diplom_
