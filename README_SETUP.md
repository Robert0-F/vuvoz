# Настройка демо-данных и развёртывание на сервере

Пошаговая инструкция: **очистить базу** → **создать суперпользователя** → **загрузить демо-данные** → **развернуть на сервере**.

Логины тестовых пользователей: [docs/DEMO_USERS.md](docs/DEMO_USERS.md) (пароль `test123`).

---

## Часть 1. Полная очистка базы данных

Выберите способ в зависимости от окружения.

### Вариант A — Django flush (рекомендуется)

Удаляет **все** строки из всех таблиц, структура (миграции) сохраняется.

```bash
cd /path/to/vuvoz   # каталог с manage.py

# Остановите Gunicorn, если на сервере:
# sudo systemctl stop vuvoz

python manage.py flush --no-input
```

После `flush` в БД не останется ни пользователей, ни заявок.

### Вариант B — PostgreSQL: пересоздать базу

Если нужна «чистая» база с нуля (например, после экспериментов):

```bash
sudo -u postgres psql <<'SQL'
DROP DATABASE IF EXISTS vuvoz;
CREATE DATABASE vuvoz OWNER vuvoz_user;
SQL

python manage.py migrate --noinput
```

Имена `vuvoz` / `vuvoz_user` замените на свои из `DATABASE_URL` в `.env`.

### Вариант C — SQLite (локальная разработка)

```bash
rm -f db.sqlite3
python manage.py migrate
```

---

## Часть 2. Создание суперпользователя

После очистки БД:

```bash
python manage.py createsuperuser
```

Введите email (будет использоваться как логин), имя и **свой** пароль администратора.  
Этот пользователь — для `/admin/` и роли администратора на сайте. Скрипт демо-данных его **не создаёт**.

Проверка миграций (если после flush или новой БД):

```bash
python manage.py migrate --noinput
```

---

## Часть 3. Загрузка демо-данных (2 компании, 12 учреждений, год истории)

Скрипт `scripts/seed_demo_year.py` создаёт:

- **2 компании** и **12 учреждений** (по 6 на компанию)
- **9 материалов** с ценами **10–20 руб/кг**
- **Завершённые заявки** с полным набором материалов у каждого учреждения
- Дополнительные заявки за **~12 месяцев** (завершённые + текущие новые/принятые)
- Пароль всех тестовых пользователей: **`test123`**

### Локально (DJANGO_DEBUG=True)

```bash
python scripts/seed_demo_year.py
```

### На тестовом сервере (production)

```bash
DEMO_SEED_ALLOW_PRODUCTION=1 python scripts/seed_demo_year.py
```

Если в БД уже есть заявки и вы хотите добавить данные поверх (не рекомендуется):

```bash
DEMO_SEED_ALLOW_PRODUCTION=1 DEMO_SEED_FORCE=1 python scripts/seed_demo_year.py
```

Список логинов: [docs/DEMO_USERS.md](docs/DEMO_USERS.md).

---

## Часть 4. Развёртывание на сервере

Ниже — сжатая версия того, как вы уже разворачивали проект. Подробности: [DEPLOYMENT.md](DEPLOYMENT.md).

### 4.1. Подготовка сервера (Ubuntu)

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib git

# Node.js 20 (для сборки фронтенда)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v   # v18+ или v20+
```

### 4.2. PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE USER vuvoz_user WITH PASSWORD 'ВАШ_ПАРОЛЬ';
CREATE DATABASE vuvoz OWNER vuvoz_user;
GRANT ALL PRIVILEGES ON DATABASE vuvoz TO vuvoz_user;
SQL
```

### 4.3. Клонирование и виртуальное окружение

```bash
cd /var/www
sudo git clone https://github.com/YOUR_ORG/vuvoz.git
sudo chown -R $USER:$USER vuvoz
cd vuvoz

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4.4. Файл `.env`

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

Минимум для production:

```bash
DJANGO_SECRET_KEY=...          # openssl rand -base64 50
DJANGO_DEBUG=False
DATABASE_URL=postgres://vuvoz_user:ВАШ_ПАРОЛЬ@localhost:5432/vuvoz
ALLOWED_HOSTS=ваш-домен.ru,www.ваш-домен.ru,IP_СЕРВЕРА
CORS_ALLOWED_ORIGINS=https://ваш-домен.ru
CSRF_TRUSTED_ORIGINS=https://ваш-домен.ru
BASE_URL=https://ваш-домен.ru
SECURE_SSL_REDIRECT=False      # True после certbot
```

Проверка:

```bash
python scripts/check_env.py
```

### 4.5. Миграции, фронтенд, статика

```bash
source .venv/bin/activate
python manage.py migrate --noinput

bash build_frontend.sh
python manage.py collectstatic --noinput
```

**Медиа:** папка `media/` не в git. Скопируйте с dev-машины фото материалов/товаров или загрузите через админку.  
Логотипы бренда уже в `frontend/src/assets/brand/` и попадают в сборку автоматически.

### 4.6. Демо-данные на сервере

```bash
python manage.py flush --no-input
python manage.py createsuperuser
DEMO_SEED_ALLOW_PRODUCTION=1 python scripts/seed_demo_year.py
```

### 4.7. Gunicorn (systemd)

Файл `/etc/systemd/system/vuvoz.service`:

```ini
[Unit]
Description=Vuvoz Gunicorn
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vuvoz
EnvironmentFile=/var/www/vuvoz/.env
ExecStart=/var/www/vuvoz/.venv/bin/gunicorn vuvoz.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 4 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable vuvoz
sudo systemctl start vuvoz
sudo systemctl status vuvoz
```

Права на каталог (если Gunicorn под `www-data`):

```bash
sudo chown -R www-data:www-data /var/www/vuvoz/media /var/www/vuvoz/staticfiles
```

### 4.8. Nginx

Скопируйте и отредактируйте [deploy/nginx-vuvoz-site.conf](deploy/nginx-vuvoz-site.conf):

```bash
sudo cp deploy/nginx-vuvoz-site.conf /etc/nginx/sites-available/vuvoz
sudo nano /etc/nginx/sites-available/vuvoz
# Замените server_name и пути /var/www/vuvoz

sudo ln -sf /etc/nginx/sites-available/vuvoz /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 4.9. SSL (после проверки по HTTP)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.ru -d www.ваш-домен.ru
```

В `.env` включите `SECURE_SSL_REDIRECT=True`, обновите CORS/CSRF на `https://`, перезапустите:

```bash
sudo systemctl restart vuvoz
```

### 4.10. Обновление после `git pull`

```bash
cd /var/www/vuvoz
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate --noinput
bash build_frontend.sh
python manage.py collectstatic --noinput
sudo systemctl restart vuvoz
```

### 4.11. Проверка

```bash
python manage.py check
python -m pytest tests/ -q
curl -I http://127.0.0.1:8000/api/
```

В браузере: главная страница, вход `company1@test.com` / `test123`, статистика за «1 год».

---

## Краткая шпаргалка (всё подряд)

```bash
# 1. Очистка
python manage.py flush --no-input

# 2. Админ
python manage.py createsuperuser

# 3. Демо-данные
DEMO_SEED_ALLOW_PRODUCTION=1 python scripts/seed_demo_year.py

# 4. Перезапуск (на сервере)
sudo systemctl restart vuvoz
```

Логины: [docs/DEMO_USERS.md](docs/DEMO_USERS.md).
