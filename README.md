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

- **API**: http://localhost:8000/api/ (проверка: http://localhost:8000/api/health/)
- **Frontend**: http://localhost:5173 (прокси `/api` на 8000). Открывайте сайт по этому адресу, не по 8000.

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
├── scripts/             # load_test_data.py, clear_db.py, health_check.py
├── docs/                # Чек-листы и доп. документация
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```
