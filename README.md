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

- **API**: http://localhost:8000/api/
- **Frontend**: http://localhost:5173 (прокси `/api` на 8000)

### Тестовые данные

```bash
python -c "exec(open('setup_dev_data.py').read()); run()"
```

- **Администратор**: `admin@test.com` / `test123`
- **Компания**: `company@test.com` / `test123`
- **Учреждение**: `school1@test.com` / `test123`

## Тесты

```bash
pytest tests/ -v
```

## Документация

- [DEPLOYMENT.md](DEPLOYMENT.md) — развёртывание, Nginx, Gunicorn, Docker
- [API_DOCS.md](API_DOCS.md) — описание всех API-эндпоинтов
- [PROJECT_STATUS.md](PROJECT_STATUS.md) — статус проекта, известные проблемы

## Структура проекта

```
vuvoz/
├── collection/          # Django app (модели, views, serializers)
├── vuvoz/               # Django settings, urls
├── frontend/            # Vue SPA (Vite, Vuetify)
├── tests/               # Pytest тесты API
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```
