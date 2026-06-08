# Vuvoz — Waste Paper Collection Service

Сервис для организации сбора макулатуры: компании-сборщики управляют учреждениями и заявками, учреждения создают заявки на вывоз, администраторы управляют прайс-листами и новостями.

## Возможности

- **Публичная главная страница** — hero, интерактивный калькулятор доходности, для кого / как работает / преимущества, отзывы, новости, финальный CTA, регистрация учреждений
- **Роли пользователей**: Администратор, Компания, Учреждение
- **Компании** — управление профилем, учреждениями, заявками, статистика
- **Учреждения** — создание заявок на вывоз, просмотр своей статистики
- **Администраторы** — управление компаниями, прайс-листами, новостями, статистика, заявки на регистрацию
- **Новости** — публичная лента (без авторизации) + CRUD для админов

## Технологии

- **Backend**: Django 4.2+, DRF, JWT (Simple JWT), PostgreSQL / SQLite
- **Frontend**: Vue 3, Vuetify 3, TypeScript, Vite

## Секреты и `.env`

Все пароли и ключи — **только** в файле `.env` в корне проекта (не коммитится).

```bash
cp .env.example .env
# Заполните CHANGE_ME: DJANGO_SECRET_KEY, DATABASE_URL, POSTGRES_PASSWORD, SMTP и домены
chmod 600 .env   # на Linux-сервере
python scripts/check_env.py   # проверка перед production
```

- Шаблон: [`.env.example`](.env.example) — в git, без реальных секретов.
- Django и Vite (переменные `VITE_*`) читают **один** корневой `.env`.
- Пароли пользователей сайта (admin, school01…) в `.env` не хранятся — только в БД.
- Если SSH-ключ когда-либо попадал в git — сгенерируйте новый на сервере.
- Пример SQL для PostgreSQL без пароля: [`robert.md.example`](robert.md.example).

## Демо-данные и развёртывание на сервере

Полная инструкция: очистка БД, суперпользователь, загрузка тестовых данных (2 компании, 12 учреждений, год истории), деплой — **[README_SETUP.md](README_SETUP.md)**.  
Логины тестовых пользователей (пароль `test123`): **[docs/DEMO_USERS.md](docs/DEMO_USERS.md)**.

## Быстрый старт

### Локальная разработка

```bash
cp .env.example .env
# Для dev: DJANGO_DEBUG=True, DEV_TEST_PASSWORD=test123 (опционально)

# Backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (отдельный терминал)
cd frontend && npm install && npm run dev
```

- **API**: http://localhost:8000/api/ (проверка: http://localhost:8000/api/health/). Браузерный интерфейс DRF со стилями доступен и по http://localhost:5173/api/… (прокси `/api`, `/media`, `/static` на 8000).
- **Frontend**: http://localhost:5173. Открывайте сайт по этому адресу; фото товаров (баллы) подгружаются с 8000 (`BASE_URL` в dev указывает на backend).

Если Vue не подключается к Django (страницы не загружаются, запросы не проходят) — см. [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

### Локальная разработка в Docker + PostgreSQL

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py createsuperuser
```

- Приложение: `http://localhost`
- PostgreSQL: контейнер `db` (данные в `postgres_data`)
- SMTP для разработки: Mailpit `http://localhost:8025` (контейнер `mailpit`)

Остановка:

```bash
docker compose down
```

### Тестовые данные

**Минимальный набор** (админ + одна компания + одно учреждение):

```bash
python -c "exec(open('setup_dev_data.py').read()); run()"
```

Пароль тестовых пользователей — из `.env` (`DEV_TEST_PASSWORD`, по умолчанию `test123`). Скрипты не запускаются при `DJANGO_DEBUG=False`.

- Администратор: `admin@test.com`
- Компания: `company@test.com`
- Учреждение: `school1@test.com` (и др.)

**Полный набор** (2 компании, 20 организаций с русскими названиями, 40 заявок — новые и завершённые). Запуск из корня проекта:

```bash
python scripts/load_test_data.py
```

Или через shell (обязательно `encoding='utf-8'` для корректных русских названий):

```bash
python manage.py shell -c "exec(open('scripts/load_test_data.py', encoding='utf-8').read()); run()"
```

- Компании: `company1@test.com`, `company2@test.com` / `test123`
- Организации: школы, офисы, магазины, производство (логин = email организации, пароль `test123`). См. [docs/INTERFACE_TEST_CHECKLIST.md](docs/INTERFACE_TEST_CHECKLIST.md).

**Товары за баллы** — создать 10 тестовых товаров: `python scripts/create_bonus_products.py`.

**Данные для статистики** — для проверки вкладки «Статистика» в админке:
```bash
python scripts/generate_stats_data.py
```
Создаёт ~60 заявок с разными датами, типами макулатуры и статусами (требуется `load_test_data.py`).

**Фото товаров** — сохраняются в `media/products/`. Чтобы хотя бы один товар показывал фото: загрузите в **Django admin** (http://localhost:8000/admin/ → «Товары (баллы)») или выполните скрипт (после `create_bonus_products.py`):

```bash
python scripts/attach_test_product_image.py
```

> **Примечание**: Загрузка фото из Vue-админки (вкладка «Товары») может не сохраняться — см. [PROJECT_STATUS.md](PROJECT_STATUS.md). Пока используйте Django admin или скрипт.

**Очистка базы** (оставить только админ):

```bash
python scripts/clear_db.py
```

### Скрипты для работы с базой данных

**1. Сохранить базу (резервная копия)**

```bash
python scripts/backup_db.py
```

- **SQLite**: копирует `db.sqlite3` в каталог `backups/` с именем `db_YYYYMMDD_HHMMSS.sqlite3`.
- **PostgreSQL**: создаёт дамп в `backups/vuvoz_YYYYMMDD_HHMMSS.sql` (нужен `pg_dump` в PATH).
- Можно указать свой каталог: `python scripts/backup_db.py C:\my_backups`.

**2. Удалить все данные из базы**

Полная очистка (включая всех пользователей и админа):

```bash
python scripts/wipe_db.py
```

Перед запуском желательно сделать резервную копию: `python scripts/backup_db.py`.

**3. Полный набор тестовых данных** (админ, 8 компаний, 80 организаций, заявки за год)

Создаёт: одного администратора, 8 компаний, 80 организаций (все данные на русском), по 20 завершённых и 1 активной заявке на каждую организацию. Даты завершённых заявок распределены по последнему году — удобно для проверки статистики и графиков.

Типы организаций: школы, офисы, производство, частные клиенты (у частных клиентов в названии указано ФИО, например «Иванов Иван Иванович»).

```bash
python scripts/create_full_test_data.py
```

Или через shell (для корректной кодировки русского текста):

```bash
python manage.py shell -c "exec(open('scripts/create_full_test_data.py', encoding='utf-8').read()); run()"
```

Рекомендуемый порядок для чистой базы: сначала полная очистка, затем создание тестовых данных:

```bash
python scripts/backup_db.py
python scripts/wipe_db.py
python scripts/create_full_test_data.py
```

- Администратор: `admin@vuvoz.ru` / `test123`
- Компании: `company1@test.com` … `company8@test.com` / `test123`
- Организации: `school01@test.com`, `office01@test.com`, `factory01@test.com`, `private01@test.com` и т.д. / `test123`

## Тесты

```bash
pytest tests/ -v
```

Ожидается 21 тест (API, лимиты веса, валидация заявок, профиль учреждения).

## Production

Развёртывание в production (Docker, Nginx + Gunicorn, переменные окружения, SSL): см. [DEPLOYMENT.md](DEPLOYMENT.md). Итоги предзапускного аудита — [DEPLOYMENT_AUDIT.md](DEPLOYMENT_AUDIT.md).

## Документация

- [DEPLOYMENT.md](DEPLOYMENT.md) — развёртывание, Nginx, Gunicorn, Docker
- [DEPLOYMENT_AUDIT.md](DEPLOYMENT_AUDIT.md) — отчёт предзапускного аудита (production readiness)
- [API_DOCS.md](API_DOCS.md) — описание всех API-эндпоинтов
- [PROJECT_STATUS.md](PROJECT_STATUS.md) — статус проекта, известные проблемы, [Future Ideas / Roadmap](PROJECT_STATUS.md#future-ideas--roadmap)
- [docs/INTERFACE_TEST_CHECKLIST.md](docs/INTERFACE_TEST_CHECKLIST.md) — чек-лист ручной проверки интерфейса
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — если Vue не подключается к Django, страницы не загружаются
- [docs/STATISTICS_LOGIC.md](docs/STATISTICS_LOGIC.md) — логика статистики в админке (откуда данные, период по созданию/завершению)

## Структура проекта

```
vuvoz/
├── collection/          # Django app (модели, views, serializers)
├── vuvoz/               # Django settings, urls
├── frontend/            # Vue SPA (Vite, Vuetify)
├── tests/               # Pytest тесты API
├── scripts/             # backup_db.py, wipe_db.py, create_full_test_data.py, load_test_data.py, clear_db.py, create_bonus_products.py, …
├── docs/                # Чек-листы и доп. документация
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```
