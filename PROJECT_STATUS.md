# Project Status — Vuvoz

## Текущий статус

- **Версия**: 1.0
- **Тесты**: 21 тест, все проходят (API, лимиты веса, валидация заявок, профиль учреждения)
- **Backend**: Django 4.2+, DRF, JWT, PostgreSQL/SQLite
- **Frontend**: Vue 3, Vuetify 3, TypeScript, Vite

## Реализованные функции

- [x] Публичная главная страница с лентой новостей
- [x] JWT-аутентификация
- [x] Роли: Администратор, Компания, Учреждение
- [x] Профили компаний и учреждений (в т.ч. редактирование контактов учреждения)
- [x] Заявки на сбор (с материалами, статусами, лимитами мин/макс веса)
- [x] Прайс-листы
- [x] Новости (публичный доступ + CRUD для админов)
- [x] Зелёные баллы: каталог товаров, заказы, история начислений/трат
- [x] Уведомления
- [x] Статистика для компаний и учреждений
- [x] Docker (PostgreSQL + Django + Nginx)
- [x] Скрипты тестовых данных, очистки БД и тестового фото товара (`scripts/load_test_data.py`, `scripts/clear_db.py`, `scripts/create_bonus_products.py`, `scripts/attach_test_product_image.py`)
- [x] Единообразный UI: отступы шапки, скругление и тени карточек; чек-лист проверки интерфейса

## Последние изменения (для релиза / проверки на другой машине)

- **Тесты**: добавлены тесты лимитов веса (GET `/api/weight-limits/`, валидация мин/макс при создании заявки), тесты обновления профиля учреждения (контакт, телефон). Всего 21 тест. Запуск: `pytest tests/ -v`.
- **UI**: отступы шапки (px-4 py-2) и скругление карточек (rounded-lg, elevation-1) во всех дашбордах и на главной/новостях.
- **Скрипты**:
  - `scripts/load_test_data.py` — 2 компании, 20 организаций (школы, офисы, магазины, производство) с русскими названиями, по 1 новой и 1 завершённой заявке на организацию (40 заявок). Запуск из корня: `python scripts/load_test_data.py`. Файл в UTF-8.
  - `scripts/clear_db.py` — очистка БД с сохранением только суперпользователей (админ). Запуск: `python scripts/clear_db.py`.
- **Зелёные баллы**: каталог товаров (Product), заказы (PointsOrder), история в `/api/me/points/`; админ управляет товарами и статусами заказов; учреждения заказывают за баллы. API: `/api/products/`, `/api/points-orders/`.
- **Фото товаров**: `Product.image` (ImageField), `image_url` в API; фото в `media/products/`; Vite проксирует `/media` и `/static` на Django.
- **Документация**: README, API_DOCS, TROUBLESHOOTING, [docs/INTERFACE_TEST_CHECKLIST.md](docs/INTERFACE_TEST_CHECKLIST.md).

## Известные проблемы / TODOs

| # | Описание | Приоритет |
|---|----------|-----------|
| 1 | NewsArticle.image — FileField вместо ImageField (Pillow не обязателен) | Низкий |
| 2 | **Загрузка фото товара из админ-интерфейса (Vue) может не сохраняться** — временно загружать через Django admin или `scripts/attach_test_product_image.py` | Высокий |
| 3 | Rate limiting не настроен | Средний |
| 4 | Нет Vue-компонентных тестов | Низкий |

## Технический долг

- Дублирование `validate_inn`/`validate_kpp` в InstitutionProfileSerializer
- Postman-коллекция устарела: нет endpoints для news, material_lines, products, points-orders

## Рекомендации

1. Добавить rate limiting (DRF throttling) для защиты от brute-force
2. Настроить Sentry или аналог для логирования ошибок
3. Добавить health-check endpoint (`/api/health/`)
4. Рассмотреть ImageField + Pillow для NewsArticle.image

## Roadmap

- [ ] Email-уведомления при смене статуса заявки
- [ ] Экспорт заявок в Excel/PDF
- [ ] Мобильное приложение / PWA
- [ ] Мультиязычность (en)
