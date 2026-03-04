# Deployment Guide — Vuvoz

## Содержание

1. [Локальная разработка](#локальная-разработка)
2. [Production — один сервер](#production--один-сервер)
3. [Production — Nginx + Gunicorn](#production--nginx--gunicorn)
4. [Docker (PostgreSQL + Django + Nginx)](#docker-postgresql--django--nginx)
5. [Привязка домена (общая)](#привязка-домена-общая)
6. [База данных — backup и restore](#база-данных--backup-и-restore)
7. [SSL-сертификаты](#ssl-сертификаты)
8. [Чек-лист развёртывания](#чек-лист-развёртывания)

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

---

## Production — один сервер

Django отдаёт SPA и статику. Gunicorn слушает порт 8000.

### 1. Сборка фронтенда и статики

```bash
bash build_frontend.sh
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

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

### 3. Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django |
| `DJANGO_DEBUG` | `False` в production |
| `ALLOWED_HOSTS` | `example.com,www.example.com` |
| `DATABASE_URL` | `postgres://user:pass@host:5432/dbname` |
| `CORS_ALLOWED_ORIGINS` | `https://example.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://example.com` |
| `EMAIL_BACKEND` | SMTP backend для писем |

---

## Production — Nginx + Gunicorn

### Nginx (пример конфига)

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;
    client_max_body_size 10M;

    location /static/ {
        alias /var/www/vuvoz/staticfiles/;
    }

    location /media/ {
        alias /var/www/vuvoz/media/;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
    }

    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

### Systemd unit (gunicorn)

`/etc/systemd/system/vuvoz.service`:

```ini
[Unit]
Description=Vuvoz Gunicorn
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vuvoz
Environment="PATH=/var/www/vuvoz/venv/bin"
EnvironmentFile=/var/www/vuvoz/.env
ExecStart=/var/www/vuvoz/venv/bin/gunicorn vuvoz.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable vuvoz
sudo systemctl start vuvoz
```

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

Соберите фронтенд и статику, настройте Nginx с `server_name 85.239.40.127;` и проксированием на Gunicorn. В systemd или при запуске Gunicorn передайте те же переменные окружения. Подробнее — секции [Production — один сервер](#production--один-сервер) и [Production — Nginx + Gunicorn](#production--nginx--gunicorn).

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

---

## SSL-сертификаты

### Certbot (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

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
