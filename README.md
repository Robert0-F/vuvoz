# Vuvoz — Waste Paper Collection Service

Сервис для организации сбора макулатуры: компании-сборщики управляют учреждениями и заявками, учреждения создают заявки на вывоз, администраторы управляют прайс-листами и новостями.

## Возможности

- **Публичная главная страница** — лента новостей, описание сервиса, кнопка входа
- **Роли пользователей**: Администратор, Компания, Учреждение
- **Компании** — управление профилем, учреждениями, заявками, статистика
- **Учреждения** — создание заявок на вывоз, просмотр своей статистики
- **Администраторы** — управление компаниями, прайс-листами, новостями
- **Новости** — публичная лента (без авторизации) + CRUD для админов

## Технологии

- **Backend**: Django 4.2+, DRF, JWT (Simple JWT), PostgreSQL / SQLite
- **Frontend**: Vue 3, Vuetify 3, TypeScript, Vite

## Быстрый старт

### Локальная разработка

```bash
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

### Тестовые данные

**Минимальный набор** (админ + одна компания + одно учреждение):

```bash
python -c "exec(open('setup_dev_data.py').read()); run()"
```

- Администратор: `admin@test.com` / `test123`
- Компания: `company@test.com` / `test123`
- Учреждение: `school1@test.com` / `test123`

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

**Фото товаров** — сохраняются в `media/products/`. Чтобы хотя бы один товар показывал фото: загрузите в **Django admin** (http://localhost:8000/admin/ → «Товары (баллы)») или выполните скрипт (после `create_bonus_products.py`):

```bash
python scripts/attach_test_product_image.py
```

> **Примечание**: Загрузка фото из Vue-админки (вкладка «Товары») может не сохраняться — см. [PROJECT_STATUS.md](PROJECT_STATUS.md). Пока используйте Django admin или скрипт.

**Очистка базы** (оставить только админ):

```bash
python scripts/clear_db.py
```

## Тесты

```bash
pytest tests/ -v
```

Ожидается 21 тест (API, лимиты веса, валидация заявок, профиль учреждения).

## Документация

- [DEPLOYMENT.md](DEPLOYMENT.md) — развёртывание, Nginx, Gunicorn, Docker
- [API_DOCS.md](API_DOCS.md) — описание всех API-эндпоинтов
- [PROJECT_STATUS.md](PROJECT_STATUS.md) — статус проекта, известные проблемы
- [docs/INTERFACE_TEST_CHECKLIST.md](docs/INTERFACE_TEST_CHECKLIST.md) — чек-лист ручной проверки интерфейса
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — если Vue не подключается к Django, страницы не загружаются

## Структура проекта

```
vuvoz/
├── collection/          # Django app (модели, views, serializers)
├── vuvoz/               # Django settings, urls
├── frontend/            # Vue SPA (Vite, Vuetify)
├── tests/               # Pytest тесты API
├── scripts/             # load_test_data.py, clear_db.py, create_bonus_products.py, attach_test_product_image.py
├── docs/                # Чек-листы и доп. документация
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```
