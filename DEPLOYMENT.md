# Deployment Guide — Vuvoz

## Содержание

1. [Локальная разработка](#локальная-разработка)
2. [Production — один сервер (Gunicorn)](#production--один-сервер-gunicorn)
3. [Подключение PostgreSQL на сервере](#подключение-postgresql-на-сервере)
4. [Подключение домена (пошагово)](#подключение-домена-пошагово)
5. [Production — Nginx + Gunicorn (полная настройка)](#production--nginx--gunicorn-полная-настройка)
6. [Docker (PostgreSQL + Django + Nginx)](#docker-postgresql--django--nginx)
7. [Привязка домена (общая)](#привязка-домена-общая)
8. [База данных — backup и restore](#база-данных--backup-и-restore)
9. [SSL-сертификаты](#ssl-сертификаты)
10. [Чек-лист развёртывания](#чек-лист-развёртывания)

---

## Локальная разработка

### Backend

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (отдельный терминал)

```bash
cd frontend && npm install && npm run dev
```

- **Frontend**: http://localhost:5173 (Vite проксирует `/api` на 8000)
- **API**: http://localhost:8000/api/

### Тестовые данные

```bash
python -c "exec(open('setup_dev_data.py').read()); run()"
```

### Тесты (перед деплоем)

```bash
pip install -r requirements.txt
python manage.py check
python -m pytest tests/ -v
cd frontend && npm ci && npm run build
```

Тесты используют SQLite (`vuvoz/settings_test.py`), production — PostgreSQL из `.env`.

---

## Production — один сервер (Gunicorn)

Django отдаёт SPA и статику. Gunicorn слушает порт 8000.

### 1. Сборка фронтенда и статики

На сервере нужен **Node.js 18+** (Vite 5 не работает на Node 10/12). Установка на Ubuntu:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v   # должно быть v18.x или v20.x
```

Затем:

```bash
bash build_frontend.sh
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

**Логотипы и дизайн:** файлы бренда лежат в `frontend/src/assets/brand/` (в git) и попадают в сборку через Vite — после `collectstatic` отображаются по `/static/assets/...`. Папка `media/` в git не коммитится: на сервере нужны загруженные фото материалов/товаров (скопировать с dev или залить через админку). Скрипт `build_frontend.sh` при наличии `media/products/Green Modern Ecological Solutions Earth Company Logo.png` обновляет hero-логотип на главной.

Если при сборке появляется ошибка `Cannot find module @rollup/rollup-linux-x64-gnu` — скрипт `build_frontend.sh` на Linux сам выполняет обход (чистая установка зависимостей под текущую платформу). Запустите `bash build_frontend.sh` ещё раз.

### 2. Запуск Gunicorn

```bash
gunicorn vuvoz.wsgi:application --bind 0.0.0.0:8000
```

Рекомендуемые флаги:

```bash
gunicorn vuvoz.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### 3. Переменные окружения (единый файл `.env`)

Скопируйте [`.env.example`](.env.example) в `.env` в каталоге с `manage.py`, заполните все `CHANGE_ME`, на сервере:

```bash
chmod 600 .env
python scripts/check_env.py
```

Gunicorn читает переменные через `EnvironmentFile=/path/to/.env` (см. systemd ниже). Файл `.env` **не коммитится**.

| Переменная | Описание |
|------------|----------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django (`openssl rand -base64 50`) |
| `DJANGO_DEBUG` | `False` в production |
| `DATABASE_URL` | **Обязательно** для Gunicorn: `postgres://user:pass@localhost:5432/dbname` |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Для документации / Docker / `pg_dump` |
| `ALLOWED_HOSTS` | `example.com,www.example.com,IP` |
| `CORS_ALLOWED_ORIGINS` | `https://example.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://example.com` |
| `BASE_URL` | Публичный URL сайта |
| `SECURE_SSL_REDIRECT` | `False` до Certbot, затем `True` |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | SMTP |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Опционально |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Опционально |
| `AUDIT_LOG_RETENTION_DAYS` | Срок хранения аудита (например `180`) |
| `DEV_TEST_PASSWORD` | **Только dev**, не задавать на production |
| `VITE_API_BASE` | Для Vite dev (обычно `/api`) |

Полный список с комментариями — в [`.env.example`](.env.example). Пример SQL без пароля: [`robert.md.example`](robert.md.example).

---

## Подключение PostgreSQL на сервере

Если PostgreSQL установлен на том же сервере (не в Docker), подключите к нему Django так.

### 1. Установка PostgreSQL (Ubuntu)

Если ещё не установлен:

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 2. Создание базы и пользователя

Подключитесь под пользователем `postgres` и создайте БД и пользователя для приложения:

```bash
sudo -u postgres psql
```

В консоли PostgreSQL:

```sql
CREATE USER vuvoz_user WITH PASSWORD 'ваш_надёжный_пароль';
CREATE DATABASE vuvoz_db OWNER vuvoz_user ENCODING 'UTF8';
\q
```

(Замените `ваш_надёжный_пароль` на свой пароль; логин и имя БД можно изменить, тогда те же значения укажите в `DATABASE_URL`.)

### 3. Переменная DATABASE_URL в .env

В каталоге проекта (например `/var/www/vuvoz`) в файле `.env` задайте:

```bash
DATABASE_URL=postgres://vuvoz_user:ваш_надёжный_пароль@localhost:5432/vuvoz_db
```

Формат: `postgres://USER:PASSWORD@HOST:PORT/DATABASE`. Если PostgreSQL слушает сокет — используйте `localhost`; при подключении по сети укажите IP или hostname.

### 4. Зависимости и миграции

Убедитесь, что установлены зависимости (в т.ч. `psycopg2`/`psycopg2-binary` и `dj-database-url`):

```bash
cd /var/www/vuvoz
source .venv/bin/activate   # или: .venv\Scripts\activate на Windows
pip install -r requirements.txt
python manage.py migrate --noinput
```

При необходимости создайте суперпользователя:

```bash
python manage.py createsuperuser
```

### 5. Запуск Gunicorn с .env

Gunicorn не читает `.env` сам. Передайте переменные при запуске, например через `systemd` (файл окружения) или так:

```bash
export $(grep -v '^#' .env | xargs)
gunicorn vuvoz.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

Либо используйте `envfile` в systemd (см. [Production — Nginx + Gunicorn](#production--nginx--gunicorn)).

После этого Django будет использовать PostgreSQL. Резервное копирование — в разделе [База данных — backup и restore](#база-данных--backup-и-restore).

---

## Подключение домена (пошагово)

Пошаговая привязка домена (например, **zeleniyschet.online**) к уже работающему проекту на сервере с Gunicorn. Меняйте только конфигурацию и переменные окружения, без правок кода, если не указано иное.

### 1. DNS

У регистратора домена создайте **A-запись**: имя хоста (например `@` для корня или `www`) → IP вашего сервера (например `85.239.40.127`). Дождитесь обновления DNS (от нескольких минут до 24–48 часов). Проверка: `dig zeleniyschet.online` или `nslookup zeleniyschet.online`.

### 2. Переменные окружения (.env)

В каталоге проекта на сервере отредактируйте `.env` и укажите домен (сначала по HTTP, после включения SSL — см. п. 5):

```bash
ALLOWED_HOSTS=zeleniyschet.online,www.zeleniyschet.online,85.239.40.127,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://zeleniyschet.online,https://www.zeleniyschet.online
CSRF_TRUSTED_ORIGINS=https://zeleniyschet.online,https://www.zeleniyschet.online
```

До выдачи SSL-сертификата для проверки по HTTP можно временно использовать `http://zeleniyschet.online` и `http://www.zeleniyschet.online` в `CORS_ALLOWED_ORIGINS` и `CSRF_TRUSTED_ORIGINS`. После включения HTTPS замените на `https://...`.

### 3. Nginx

Если Nginx ещё не настроен, выполните полную настройку по разделу [Production — Nginx + Gunicorn (полная настройка)](#production--nginx--gunicorn-полная-настройка): установка Nginx, конфиг с `server_name zeleniyschet.online www.zeleniyschet.online`, и systemd для Gunicorn.

Если Nginx уже стоит и проксирует на Gunicorn, в конфиге сайта укажите домен:

```nginx
server_name zeleniyschet.online www.zeleniyschet.online;
```

Затем:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 4. Перезапуск Gunicorn

Перезапустите приложение, чтобы подхватить новые `ALLOWED_HOSTS` и CORS/CSRF:

```bash
sudo systemctl restart vuvoz
```

(или как у вас называется unit Gunicorn). Если запускаете вручную — остановите процесс и снова выполните команду с загруженным `.env`.

### 5. SSL (HTTPS)

После того как сайт открывается по `http://zeleniyschet.online`, установите сертификат (см. [SSL-сертификаты](#ssl-сертификаты)):

```bash
sudo certbot --nginx -d zeleniyschet.online -d www.zeleniyschet.online
```

Убедитесь, что в `.env` в `CORS_ALLOWED_ORIGINS` и `CSRF_TRUSTED_ORIGINS` указаны именно **https://** версии доменов, затем снова перезапустите Gunicorn.

---

## Production — Nginx + Gunicorn (полная настройка)

Ниже — пошаговая настройка, если сейчас у вас работает только Gunicorn (порт 8000), и вы хотите поставить перед ним Nginx (порты 80/443, раздача статики, проксирование на Gunicorn). В примерах путь к проекту — каталог, в котором лежат `manage.py`, `vuvoz/`, `frontend/` (например `/var/www/vuvoz` или `/var/www/vuvoz/vuvoz`). Подставьте свой путь во всех командах и конфигах. Виртуальное окружение: `.venv` (если папка называется `venv`, замените в путях).

### 1. Остановить Gunicorn на порту 8000

Если Gunicorn уже запущен и слушает `0.0.0.0:8000`, остановите его (чтобы потом запускать через systemd только на `127.0.0.1:8000`):

```bash
# Найти процесс (если запускали вручную):
sudo lsof -i :8000
# или
sudo ss -tlnp | grep 8000

# Завершить (подставьте PID из вывода):
sudo kill <PID>
```

### 2. Установить Nginx

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl enable nginx
```

### 3. Создать конфиг Nginx для сайта

Создайте файл конфигурации (например, для домена zeleniyschet.online):

```bash
sudo nano /etc/nginx/sites-available/vuvoz
```

Вставьте конфиг (замените `zeleniyschet.online` и путь `/var/www/vuvoz` при необходимости):

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name zeleniyschet.online www.zeleniyschet.online;
    client_max_body_size 10M;

    root /var/www/vuvoz/vuvoz;

    location /static/ {
        alias /var/www/vuvoz/vuvoz/staticfiles/;
    }

    location /media/ {
        alias /var/www/vuvoz/vuvoz/media/;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
        proxy_connect_timeout 10;
        proxy_send_timeout 120;
    }

    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
    }

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_intercept_errors on;
        error_page 404 = /index.html;
    }
}
```

Сохраните файл (в nano: Ctrl+O, Enter, Ctrl+X).

### 4. Включить сайт и проверить Nginx

```bash
sudo ln -sf /etc/nginx/sites-available/vuvoz /etc/nginx/sites-enabled/
# Убрать дефолтный сайт, если мешает:
# sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl reload nginx
```

### 5. Systemd-сервис для Gunicorn

Gunicorn должен слушать только **127.0.0.1:8000** (к нему обращается Nginx). Переменные окружения берём из `.env`.

Создайте unit:

```bash
sudo nano /etc/systemd/system/vuvoz.service
```

Содержимое (путь к проекту и к `.venv` проверьте):

```ini
[Unit]
Description=Vuvoz Gunicorn
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vuvoz/vuvoz
Environment="PATH=/var/www/vuvoz/vuvoz/.venv/bin"
EnvironmentFile=/var/www/vuvoz/vuvoz/.env
ExecStart=/var/www/vuvoz/vuvoz/.venv/bin/gunicorn vuvoz.wsgi:application --bind 127.0.0.1:8000 --workers 4 --threads 2 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

Если виртуальное окружение в папке `venv`, замените `.venv` на `venv` в строках `Environment` и `ExecStart`.

Права на каталог проекта и файл `.env` (Nginx/Gunicorn работают от `www-data`):

```bash
sudo chown -R www-data:www-data /var/www/vuvoz/vuvoz
# Секреты только в .env; не доступен извне (чтение для www-data через systemd)
sudo chmod 600 /var/www/vuvoz/vuvoz/.env
# Перед первым запуском: python scripts/check_env.py
```

Запуск и автозагрузка Gunicorn:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vuvoz
sudo systemctl start vuvoz
sudo systemctl status vuvoz
```

### 6. Проверка

- Сайт по HTTP: откройте в браузере `http://zeleniyschet.online` (при условии, что DNS уже указывает на сервер).
- Логи Gunicorn: `sudo journalctl -u vuvoz -f`
- Логи Nginx: `sudo tail -f /var/log/nginx/error.log`

### 7. Файрвол (по желанию)

Разрешить HTTP и HTTPS, оставив порт 8000 только для localhost:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

После этого приложение доступно снаружи только через Nginx (80/443), а Gunicorn принимает запросы только с 127.0.0.1:8000.

### 8. Устранение неполадок

**HTTP 400 Bad Request при открытии сайта**

Django возвращает 400, если заголовок `Host` запроса не входит в `ALLOWED_HOSTS`. Проверьте `.env` в каталоге проекта:

```bash
ALLOWED_HOSTS=zeleniyschet.online,www.zeleniyschet.online,localhost,127.0.0.1
```

Без пробелов после запятых. После изменения перезапустите Gunicorn:

```bash
sudo systemctl restart vuvoz
```

**В логе Nginx: `unknown directive "nginx" in .../vuvoz:2`**

В конфиге на строке 2 не должно быть слова `nginx` как директивы. Файл должен начинаться так (строка 1 — `upstream`, строка 2 — пробелы и `server`):

```nginx
upstream backend {
    server 127.0.0.1:8000;
}
```

Откройте конфиг `sudo nano /etc/nginx/sites-available/vuvoz`, удалите или исправьте вторую строку (например, ошибочно вставленный текст или комментарий без `#`), сохраните и выполните:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**Gunicorn: `Control server error: [Errno 13] Permission denied`**

Обычно это не мешает работе: воркеры запускаются, приложение отвечает. Если нужно убрать сообщение, можно задать каталог с доступными правами для `www-data`, например в unit добавить: `RuntimeDirectory=vuvoz` (и при необходимости `RuntimeDirectoryMode=0750`).

### 9. Сайт не открывается — пошаговая проверка

Если сайт перестал открываться или выдаёт 400, выполните по порядку.

**Шаг 0. Какой конфиг реально использует Nginx**

Nginx подхватывает только файлы из `sites-enabled`. Убедитесь, что там есть ваш сайт и при необходимости отключите дефолтный:

```bash
ls -la /etc/nginx/sites-enabled/
```

Должен быть симлинк на конфиг vuvoz, например: `vuvoz -> /etc/nginx/sites-available/vuvoz`. Если его нет — включите сайт:

```bash
sudo ln -sf /etc/nginx/sites-available/vuvoz /etc/nginx/sites-enabled/
```

Если в списке есть `default`, он обрабатывает запросы, когда `Host` не совпадает ни с одним `server_name`. Часто проще оставить только vuvoz на порту 80:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

После этого единственный `server` на порту 80 — ваш (zeleniyschet.online). Проверка с сервера:

```bash
curl -v -H "Host: zeleniyschet.online" http://127.0.0.1/
curl -v http://127.0.0.1:8000/
```

Первый запрос идёт в Nginx (должен ответить 200/302), второй — напрямую в Gunicorn. Если первый падает с «connection refused» или пустой ответ — Nginx не проксирует на backend. Если второй не отвечает — не запущен или не слушает Gunicorn.

**Шаг 1. Nginx запущен и конфиг корректен**

```bash
sudo systemctl status nginx
```

Если не `active (running)` — запустите: `sudo systemctl start nginx`.

Проверка конфига (должно быть «syntax is ok» и «test is successful»):

```bash
sudo nginx -t
```

Если есть ошибка (например `unknown directive "nginx"`), замените конфиг на эталонный из репозитория (без лишних строк в начале файла):

```bash
# На сервере, из каталога с клоном репозитория (путь к проекту):
sudo cp /var/www/vuvoz/vuvoz/deploy/nginx-vuvoz-site.conf /etc/nginx/sites-available/vuvoz
```

Если проект лежит в другом месте, скопируйте вручную содержимое файла `deploy/nginx-vuvoz-site.conf` из репозитория в `/etc/nginx/sites-available/vuvoz` (первая строка файла должна быть `upstream backend {`, не комментарий и не слово `nginx`). Поправьте пути и `server_name` под свой домен и каталог. Затем:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**Шаг 2. Gunicorn запущен**

```bash
sudo systemctl status vuvoz
```

Если не запущен: `sudo systemctl start vuvoz`. Рабочий каталог в unit должен быть каталог с `manage.py` (у вас: `/var/www/vuvoz/vuvoz`).

**Шаг 3. ALLOWED_HOSTS в .env**

В каталоге с `manage.py` (например `/var/www/vuvoz/vuvoz`) в `.env` должна быть строка с вашим доменом, без пробелов после запятых:

```bash
grep ALLOWED_HOSTS /var/www/vuvoz/vuvoz/.env
# Должно быть что-то вроде:
# ALLOWED_HOSTS=zeleniyschet.online,www.zeleniyschet.online,localhost,127.0.0.1
```

Если домена нет — добавьте его, сохраните файл и перезапустите Gunicorn:

```bash
sudo systemctl restart vuvoz
```

**Шаг 4. Проверка с сервера**

```bash
curl -I http://127.0.0.1:8000/
curl -I -H "Host: zeleniyschet.online" http://127.0.0.1/
```

Первый запрос проверяет Gunicorn, второй — Nginx с вашим доменом. Ожидается ответ с кодом 200 или 302, не 400.

**Если в ответе 301 и `Location: https://...`** — Django принудительно переводит на HTTPS. Пока SSL (Certbot) не настроен, сайт по HTTP будет только редиректить и в браузере не откроется. В `.env` отключите редирект и перезапустите Gunicorn:

```bash
# В .env добавить или изменить:
SECURE_SSL_REDIRECT=False
```

После настройки HTTPS (раздел [SSL-сертификаты](#ssl-сертификаты)) поставьте `SECURE_SSL_REDIRECT=True` и снова перезапустите Gunicorn.

**Шаг 5. Доступ снаружи (порт 80)**

Если с сервера (`curl -H "Host: zeleniyschet.online" http://127.0.0.1/`) всё ок, а из браузера по домену сайт не открывается — проверьте файрвол и DNS. Разрешите HTTP:

```bash
sudo ufw status
# Если 80/tcp не в списке ALLOW:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

Проверьте, что домен указывает на IP сервера: `dig zeleniyschet.online +short` или `nslookup zeleniyschet.online` — должен быть ваш серверный IP.

После этих шагов откройте в браузере `http://zeleniyschet.online`.

---

## Тестирование по IP (без домена)

Если сервер доступен по IP (например, Ubuntu с адресом **85.239.40.127**) и нужно открыть проект в браузере по `http://85.239.40.127`:

### 1. Переменные окружения

В `.env` на сервере укажите (подставьте свой IP при необходимости):

```bash
ALLOWED_HOSTS=85.239.40.127,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://85.239.40.127
CSRF_TRUSTED_ORIGINS=http://85.239.40.127
DJANGO_DEBUG=False
```

Остальные переменные — как в `.env.example` (`DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, `DATABASE_URL` при использовании Docker).

### 2. Запуск (Docker)

На сервере в каталоге проекта:

```bash
docker compose up --build -d
```

Сайт будет доступен по **http://85.239.40.127** (порт 80). Суперпользователь: `docker compose exec backend python manage.py createsuperuser`.

В `nginx.conf` можно оставить `server_name localhost;` — при одном блоке Nginx примет запросы с любым Host. Для ясности можно указать `server_name 85.239.40.127 localhost;`.

### 3. Запуск без Docker (Gunicorn + Nginx)

Соберите фронтенд и статику, настройте Nginx с `server_name 85.239.40.127;` и проксированием на Gunicorn. В systemd или при запуске Gunicorn передайте те же переменные окружения. Подробнее — секции [Production — один сервер (Gunicorn)](#production--один-сервер-gunicorn) и [Production — Nginx + Gunicorn (полная настройка)](#production--nginx--gunicorn-полная-настройка).

---

## Docker (PostgreSQL + Django + Nginx)

### 1. Подготовка .env

Скопировать из `.env.example` и задать значения:

```bash
cp .env.example .env
# Отредактировать POSTGRES_PASSWORD, DJANGO_SECRET_KEY, ALLOWED_HOSTS (и CORS/CSRF при доступе по IP или домену)
```

### 2. Запуск

```bash
docker compose up --build -d
```

Приложение доступно на порту 80. Nginx проксирует запросы на Django.
Для локальной разработки SMTP поднимается контейнер Mailpit (web UI: `http://localhost:8025`).

### 3. Production: привязка домена

Для работы по своему домену (например, `vuvoz.example.com`):

1. **DNS**: создайте A-запись, указывающую на публичный IP сервера.
2. **Переменные в `.env`** (Docker читает их и передаёт в backend):
   - `ALLOWED_HOSTS=vuvoz.example.com`
   - `CORS_ALLOWED_ORIGINS=https://vuvoz.example.com`
   - `CSRF_TRUSTED_ORIGINS=https://vuvoz.example.com`
3. **Nginx**: в `nginx.conf` замените `server_name localhost;` на `server_name vuvoz.example.com;` (в файле есть комментарий-напоминание).
4. Перезапустите контейнеры: `docker compose up -d --build`.
5. После проверки по HTTP настройте SSL (см. [SSL-сертификаты](#ssl-сертификаты)); затем добавьте `https://vuvoz.example.com` в `CORS_ALLOWED_ORIGINS` и `CSRF_TRUSTED_ORIGINS`, если ещё не добавлено.

**Создание суперпользователя (один раз):**

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Привязка домена (общая)

Независимо от способа развёртывания (Docker или Nginx + Gunicorn):

- **DNS**: A-запись вашего домена → IP сервера.
- **Django**: `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` должны содержать ваш домен (для HTTPS — с префиксом `https://`).
- **Nginx**: в конфиге указан правильный `server_name` (ваш домен).
- **SSL**: после проверки по HTTP установите сертификат (Certbot) и при необходимости обновите CORS/CSRF на `https://...`.

---

## База данных — backup и restore

### PostgreSQL

**Backup:**

```bash
pg_dump -U postgres -h localhost vuvoz_db > backup_$(date +%Y%m%d).sql
```

**Restore:**

```bash
psql -U postgres -h localhost -d vuvoz_db < backup_20250203.sql
```

### SQLite (для dev)

```bash
cp db.sqlite3 db.sqlite3.backup
```

### Аудит действий — обслуживание

Очистка старых записей аудита по сроку из `AUDIT_LOG_RETENTION_DAYS`:

```bash
python manage.py cleanup_audit_logs
```

---
http://zeleniyschet.online/
## SSL-сертификаты

### Certbot (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d zeleniyschet.online -d www.zeleniyschet.online
```
sudo certbot --nginx -d example.com -d www.example.com
Конфиг Nginx будет обновлён автоматически. Проверка автообновления:

```bash
sudo certbot renew --dry-run
```

---

## Чек-лист развёртывания

- [ ] `DJANGO_DEBUG=False`
- [ ] Уникальный `DJANGO_SECRET_KEY` (например, `openssl rand -base64 50`)
- [ ] `ALLOWED_HOSTS` = ваш домен (или несколько через запятую)
- [ ] PostgreSQL в production (не SQLite)
- [ ] `python manage.py migrate` выполнен (Docker делает при старте)
- [ ] Фронтенд собран и выполнен `collectstatic` (Docker делает при старте)
- [ ] Создан суперпользователь, если нужен доступ в Django admin
- [ ] В Nginx указан `server_name` с вашим доменом
- [ ] SSL (HTTPS) настроен
- [ ] `CORS_ALLOWED_ORIGINS` и `CSRF_TRUSTED_ORIGINS` содержат production-домен с `https://`
- [ ] Права на каталоги `staticfiles/` и `media/` для веб-сервера
