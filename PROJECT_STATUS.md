# Project Status — Vuvoz

## Текущий статус

- **Версия**: 1.0
- **Тесты**: 15 тестов, все проходят
- **Backend**: Django 4.2+, DRF, JWT, PostgreSQL/SQLite
- **Frontend**: Vue 3, Vuetify 3, TypeScript, Vite

## Реализованные функции

- [x] Публичная главная страница с лентой новостей
- [x] JWT-аутентификация
- [x] Роли: Администратор, Компания, Учреждение
- [x] Профили компаний и учреждений
- [x] Заявки на сбор (с материалами, статусами)
- [x] Прайс-листы
- [x] Новости (публичный доступ + CRUD для админов)
- [x] Уведомления
- [x] Статистика для компаний и учреждений
- [x] Docker (PostgreSQL + Django + Nginx)

## Известные проблемы / TODOs

| # | Описание | Приоритет |
|---|----------|-----------|
| 1 | NewsArticle.image — FileField вместо ImageField (Pillow не обязателен) | Низкий |
| 2 | MEDIA_URL — относительный путь `media/`; для production может потребоваться полный URL | Средний |
| 3 | Rate limiting не настроен | Средний |
| 4 | Нет Vue-компонентных тестов | Низкий |

## Технический долг

- Дублирование `validate_inn`/`validate_kpp` в InstitutionProfileSerializer
- Postman-коллекция устарела: нет endpoints для news, material_lines

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
