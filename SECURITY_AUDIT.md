# Security Audit Summary — Vuvoz

## Проверка чувствительных данных

| Область | Статус | Описание |
|---------|--------|----------|
| Секреты | OK | `SECRET_KEY` берётся из env, не в коде |
| Пароли | OK | Django `set_password`, не хранятся в plaintext |
| Токены | OK | JWT, refresh rotation |
| Логи | OK | Пароли и токены не логируются |
| .env | OK | В .gitignore, пример в .env.example |

## Валидация ввода

| Модуль | Статус | Описание |
|--------|--------|----------|
| Serializers | OK | DRF валидация, custom validators (ИНН, КПП, ОГРН, телефон) |
| Модели | OK | CharField max_length, DecimalField, EmailField |
| Validators | OK | `validate_inn`, `validate_kpp`, `validate_ogrn`, `validate_phone_ru`, `validate_paper_weight_kg` |

## Доступ к данным

| Эндпоинт | Доступ | Проверка |
|----------|--------|----------|
| News list/retrieve | Public | Только published |
| News CRUD | Admin | IsAdministrator |
| Company profiles | Company / Admin | IsOwnCompany |
| Institutions | Role-based | IsInstitutionAccess |
| Collection requests | Role-based | CanViewRequest |
| Prices | Admin / authenticated | IsAdministrator / IsAuthenticated |
| Stats | Company / Institution | IsCompanyUser / IsInstitutionUser |

## CORS и CSRF

- CORS: `CORS_ALLOWED_ORIGINS` из env
- CSRF: `CSRF_TRUSTED_ORIGINS` настроен
- Credentials: `CORS_ALLOW_CREDENTIALS = True`

## Рекомендации

1. **Production**: всегда использовать HTTPS
2. **Rate limiting**: добавить throttling на `/api/token/` и остальные эндпоинты
3. **Логирование**: не логировать пароли и токены
4. **Патчи**: регулярно обновлять зависимости
