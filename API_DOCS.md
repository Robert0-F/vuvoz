# API Documentation — Vuvoz

Базовый URL: `/api/`

## Аутентификация

### Метод: JWT (JSON Web Tokens)

Используется `djangorestframework-simplejwt`. Для защищённых эндпоинтов передавать заголовок:

```
Authorization: Bearer <access_token>
```

### Получение токена

**POST** `/api/token/`

Request:
```json
{
  "username": "company@test.com",
  "password": "test123"
}
```

Response 200:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Обновление access-токена

**POST** `/api/token/refresh/`

Request:
```json
{
  "refresh": "<refresh_token>"
}
```

Response 200:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Эндпоинты

### Текущий пользователь

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/me/` | Authenticated | Текущий пользователь и профиль |

Response 200:
```json
{
  "id": 1,
  "username": "company@test.com",
  "email": "company@test.com",
  "first_name": "",
  "last_name": "",
  "role": "company",
  "role_display": "Collection Company",
  "profile": {
    "id": 1,
    "company_name": "Test Company",
    "address": "...",
    ...
  }
}
```

---

### Новости (публичные)

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/news/` | Public | Список опубликованных новостей |
| GET | `/api/news/{id}/` | Public | Одна новость |
| POST | `/api/news/` | Admin | Создать новость |
| PUT/PATCH | `/api/news/{id}/` | Admin | Обновить новость |
| DELETE | `/api/news/{id}/` | Admin | Удалить новость |

**GET** `/api/news/` — без авторизации. Возвращает только `is_published=True`, сортировка по `created_at` descending.

Response 200:
```json
[
  {
    "id": 1,
    "title": "Заголовок",
    "content": "Текст статьи...",
    "excerpt": "Текст статьи...",
    "image": null,
    "image_url": "http://localhost:8000/media/news_images/...",
    "created_at": "2025-02-03T12:00:00Z",
    "is_published": true,
    "author": null,
    "author_username": ""
  }
]
```

**POST** `/api/news/` (Admin):
- `title` (required)
- `content` (required)
- `image` (optional, file)
- `is_published` (optional, default true)

---

### Профили компаний

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/company-profiles/` | Company / Admin | Список (своя / все) |
| GET | `/api/company-profiles/{id}/` | Company / Admin | Детали |
| POST | `/api/company-profiles/` | Admin | Создать компанию |
| PUT/PATCH | `/api/company-profiles/{id}/` | Company / Admin | Обновить |
| DELETE | `/api/company-profiles/{id}/` | Admin | Удалить |

---

### Учреждения

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/institutions/` | Company / Institution / Admin | Список |
| GET | `/api/institutions/{id}/` | Company / Institution / Admin | Детали |
| POST | `/api/institutions/` | Company / Admin | Создать учреждение |
| PUT/PATCH | `/api/institutions/{id}/` | Company / Institution / Admin | Обновить |
| DELETE | `/api/institutions/{id}/` | Company / Admin | Удалить |
| PATCH | `/api/institutions/{id}/reset_password/` | Company | Сброс пароля учреждения |

Query params для GET `/api/institutions/`: `search` — поиск по имени, типу, контакту, email.

---

### Заявки на сбор

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/collection-requests/` | Company / Institution / Admin | Список |
| GET | `/api/collection-requests/{id}/` | Company / Institution / Admin | Детали |
| POST | `/api/collection-requests/` | Institution | Создать заявку |
| PUT/PATCH | `/api/collection-requests/{id}/` | Company | Обновить (статус и т.д.) |
| DELETE | `/api/collection-requests/{id}/` | Company / Admin | Удалить |
| POST | `/api/collection-requests/{id}/complete/` | Company | Завершить заявку |
| POST | `/api/collection-requests/calculate/` | Institution | Расчёт стоимости (preview) |

Query params для GET: `status`, `start_date`, `end_date`, `institution_type`, `min_weight`, `max_weight`.

**POST** `/api/collection-requests/` (Institution):
```json
{
  "material_lines": [
    {"material_type": "paper", "amount_kg": "50"},
    {"material_type": "cardboard", "amount_kg": "30"}
  ],
  "desired_date": "2025-02-15",
  "comment": "Комментарий"
}
```

**POST** `/api/collection-requests/{id}/complete/`:
```json
{
  "actual_amount": "48.5",
  "actual_collection_date": "2025-02-14",
  "internal_notes": "Заметки"
}
```

---

### Прайс-лист

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/prices/` | Admin | Список |
| GET | `/api/prices/{id}/` | Admin | Детали |
| GET | `/api/prices/current/` | Authenticated | Текущие цены по материалам |
| POST | `/api/prices/` | Admin | Создать |
| PUT/PATCH | `/api/prices/{id}/` | Admin | Обновить |
| DELETE | `/api/prices/{id}/` | Admin | Удалить |

**GET** `/api/prices/current/`:
```json
[
  {"material_type": "paper", "material_type_display": "Бумага", "price_per_kg": "5.00"},
  {"material_type": "cardboard", "material_type_display": "Картон", "price_per_kg": "3.00"}
]
```

---

### Статистика

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/stats/company/` | Company | Статистика компании |
| GET | `/api/stats/institution/` | Institution | Статистика учреждения |

Query params: `start_date`, `end_date` (YYYY-MM-DD).

---

### Аудит действий (Admin)

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/audit-logs/` | Admin | Список логов с фильтрами и пагинацией |
| GET | `/api/audit-logs/export/?export_format=csv|txt` | Admin | Экспорт логов по фильтрам |

Query params для `/api/audit-logs/`:
- `page` (default `1`)
- `page_size` (default `25`, max `200`)
- `category` (`info` / `warning` / `critical`)
- `action_type`
- `actor_role` (`admin` / `company` / `institution`)
- `target_model`
- `date_from`, `date_to` (`YYYY-MM-DD`)
- `search` (по summary/action/model/id/username)

Response 200:
```json
{
  "count": 123,
  "page": 1,
  "page_size": 25,
  "results": [
    {
      "id": 10,
      "created_at": "2026-04-01T12:00:00Z",
      "category": "warning",
      "action_type": "reset_password",
      "actor_role": "company",
      "actor_username": "company@test.com",
      "target_model": "InstitutionProfile",
      "target_id": "5",
      "short_summary": "Institution password reset by company/admin",
      "ip_address": "127.0.0.1"
    }
  ]
}
```

---

### Информация о БД (Admin)

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/database-info/` | Admin | Показывает тип текущей БД (sqlite/postgresql), engine, name, host, port |

Response 200:
```json
{
  "db_type": "postgresql",
  "engine": "django.db.backends.postgresql",
  "name": "vuvoz",
  "host": "db",
  "port": "5432"
}
```

---

### Уведомления

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/notifications/` | Authenticated | Список уведомлений |
| GET | `/api/notifications/{id}/` | Authenticated | Детали |
| POST | `/api/notifications/{id}/mark_read/` | Authenticated | Отметить прочитанным |
| POST | `/api/notifications/mark_all_read/` | Authenticated | Отметить все прочитанными |

---

## Коды ответов

| Код | Описание |
|-----|----------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request — ошибка валидации |
| 401 | Unauthorized — требуется авторизация |
| 403 | Forbidden — нет прав |
| 404 | Not Found |
| 500 | Server Error |

## Формат ошибок

```json
{
  "detail": "Текст ошибки"
}
```

Валидация (400):
```json
{
  "field_name": ["Сообщение об ошибке"]
}
```

---

### Бонусы организаций

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/bonus-config/` | Admin | Текущий процент бонуса |
| PATCH | `/api/bonus-config/` | Admin | Изменить процент бонуса (body: `{ "bonus_percent": 1.5 }`) |
| GET | `/api/institution-bonuses/` | Admin | Список бонусов (query: `?status=pending` или `?status=confirmed`) |
| GET | `/api/institution-bonuses/<id>/` | Admin | Один бонус |
| PATCH | `/api/institution-bonuses/<id>/` | Admin | Изменить сумму к начислению и/или подтвердить (body: `{ "awarded_amount": 100, "status": "confirmed" }`) |

Бонус создаётся автоматически при переходе заявки в статус «Завершена». Сумма по умолчанию = стоимость заявки × процент. Администратор подтверждает или меняет сумму и выставляет статус `confirmed`. Все суммы бонусов — в **зелёных баллах** (не рубли).

---

### Техподдержка (админ)

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/support-config/` | Admin | Текущий глобальный специалист и число привязанных учреждений |
| PATCH | `/api/support-config/` | Admin | Назначить специалиста на все учреждения (body: `{ "support_user": <id> }`) |
| GET | `/api/support-users/` | Admin | Список аккаунтов техподдержки (в системе допускается один) |
| POST | `/api/support-users/` | Admin | Создать аккаунт support (body: `{ "email": "...", "password": "..." }`; пароль опционален — сгенерируется) |

Response `GET /api/support-config/`:
```json
{
  "id": 1,
  "support_user": 5,
  "support_username": "support@example.com",
  "support_email": "support@example.com",
  "institutions_assigned": 12
}
```

При создании support-пользователя или PATCH конфига все `InstitutionProfile.support_user` обновляются массово. Новые учреждения получают специалиста автоматически.

---

### Чат техподдержки

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/support/institutions/` | Support | Список учреждений с `unread_count`, `last_message_at`, `last_message_preview` |
| GET | `/api/support/chats/<institution_id>/` | Support / Institution | История сообщений. Query: `?limit=50` (макс. 200), `?before_id=<id>` — пагинация |
| POST | `/api/support/chats/<institution_id>/` | Support / Institution | Отправить сообщение: `{ "message": "текст" }` |
| POST | `/api/support/chats/<institution_id>/read/` | Support / Institution | Отметить входящие сообщения прочитанными |

Сообщение в ответе: `id`, `institution`, `sender`, `sender_username`, `sender_role`, `message`, `is_read`, `is_mine`, `created_at`.

Для организации в `GET /api/me/` в профиле доступны `support_user`, `support_username`, `support_unread_count` (непрочитанные ответы поддержки).

---

### Зелёные баллы (организация)

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/me/points/` | Institution | Баланс баллов и история (начисления и траты): `{ "balance": "0", "history": [{ "type": "accrual"\|"expense", "amount": "...", "date": "...", "reference": "Заявка REQ-..." \| "Заказ #1" }] }` |

### Товары за баллы

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/products/` | Auth | Список товаров (для организаций — только активные). |
| POST | `/api/products/` | Admin | Создать товар. JSON: `{ name, description, price_in_points, is_active }`. С фото: `multipart/form-data`, поле `image`. |
| GET/PATCH/DELETE | `/api/products/<id>/` | Admin | Просмотр, изменение, удаление. PATCH с фото: `multipart/form-data`. |

Ответ продукта: `id`, `name`, `description`, `image` (путь), `image_url` (абсолютный URL), `price_in_points`, `is_active`, `created_at`.

### Заказы за баллы

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/points-orders/` | Institution (свои) / Admin (все) | Список заказов. |
| POST | `/api/points-orders/` | Institution | Создать заказ: `{ "recipient_name", "recipient_phone", "address", "items": [{ "product_id": int, "quantity": int }] }`. Списываются баллы с баланса организации. |

### Статистика (админ)

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/stats/admin/` | Admin | Упрощённая сводка (legacy): материалы, топ организаций, статусы, динамика. |
| GET | `/api/analytics/dashboard/` | Admin | Полная аналитика для вкладки «Статистика». Параметры: `date_from`, `date_to`, `basis` (`created` \| `completed`), `company_id`, `institution_id`, `institution_type`, `material_type`. Ответ: `kpis`, `materials`, `requests_insights` (воронка, очередь, SLA, срочность), `public_pickup` (заявки с сайта), бонусы, топы. Подробнее: [docs/STATISTICS_LOGIC.md](docs/STATISTICS_LOGIC.md). |

---

### Публичный каталог материалов и заявки на вывоз (главная)

Без JWT. Цены берутся из активного `PriceList` для каждого активного `Material`.

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/public/materials/` | Public | Список материалов с ценой за кг, фото, описанием, порядком сортировки |
| GET | `/api/public/weight-limits/` | Public | Минимальный и максимальный вес заявки (кг) |
| POST | `/api/public/pickup-requests/` | Public | Создать заявку на вывоз с главной (калькулятор) |
| GET | `/api/public/pickup-requests/` | Admin | Список заявок на вывоз |
| PATCH | `/api/public/pickup-requests/{id}/` | Admin | Статус и заметки администратора |

**GET** `/api/public/materials/` — Response 200:
```json
[
  {
    "id": 1,
    "code": "cardboard",
    "name": "Картон",
    "short_description": "Гофрокартон",
    "icon": "package-variant",
    "image_url": "/media/materials/cardboard.jpg",
    "price_per_kg": "3.50",
    "sort_order": 1
  }
]
```

**GET** `/api/public/weight-limits/` — Response 200:
```json
{
  "min_kg": "50.00",
  "max_kg": "5000.00"
}
```

**POST** `/api/public/pickup-requests/` — Request (несколько видов сырья):
```json
{
  "items": [
    { "material_id": 1, "weight_kg": "100" },
    { "material_id": 2, "weight_kg": "50" }
  ],
  "phone": "+79991234567",
  "address": "г. Москва, ул. Примерная, 1",
  "preferred_date": "2026-05-21",
  "contact_name": "Иван (опционально)"
}
```

Response 201 — заявка с `lines[]`, `materials_summary`, `total_weight_kg`, `estimated_payout` (сумма по строкам), `status` = `new`.

Ошибки валидации: материал без цены, вес вне лимитов, дата в прошлом — 400.

**PATCH** `/api/public/pickup-requests/{id}/` (Admin) — Request (частично):
```json
{
  "status": "contacted",
  "admin_notes": "Перезвонили, вывоз в пятницу"
}
```

Статусы: `new`, `contacted`, `done`, `cancelled`.

**Материалы (админ)** — `POST`/`PATCH` `/api/materials/` поддерживают поля `short_description`, `icon`, `sort_order`, загрузку `image` (multipart/form-data).

### Регистрация с главной

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| POST | `/api/registration-requests/` | Public | Заявка учреждения (как раньше) |
| GET | `/api/registration-requests/` | Admin | Список |
| POST | `/api/company-registration-requests/` | Public | Заявка компании на вывоз |
| GET | `/api/company-registration-requests/` | Admin | Список |

**POST** `/api/company-registration-requests/`:
```json
{
  "company_name": "ООО Вывоз",
  "contact_name": "Иван",
  "phone": "+79991234567",
  "email": "info@example.com",
  "address": "Москва",
  "comment": "3 машины"
}
```

### Статистика с фильтром месяца

- **GET** `/api/stats/institution/?month=2026-05` или `start_date` + `end_date` — KPI за период, `material_breakdown`.
- **GET** `/api/stats/company/dashboard/?month=2026-05` — KPI завершённых вывозов за выбранный календарный месяц.

---

## Rate limiting

Публичные формы (`POST` pickup, registration) ограничены **30 запросов/час** с одного IP (`public_form` в `DEFAULT_THROTTLE_RATES`). При превышении — HTTP 429.

---

## Инструменты для тестирования API

### Postman

Импортировать `postman_collection.json`. Указать:
- `base_url`: `http://localhost:8000/api`
- Получить `access_token` из `POST /api/token/` и вставить в переменную.

### cURL

Получение токена:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"company@test.com","password":"test123"}'
```

Запрос с токеном:
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/me/
```
