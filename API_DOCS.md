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

---

## Rate limiting

По умолчанию ограничения не заданы. Для production рекомендуется настроить throttling (например, через `DEFAULT_THROTTLE_CLASSES` в DRF).

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
