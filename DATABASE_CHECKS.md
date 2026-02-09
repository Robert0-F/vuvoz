# Database Model Checks — Vuvoz

## CustomUser

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| username | CharField(150) | unique | да (Django default) |
| email | EmailField | - | - |
| role | CharField(20) | choices | - |
| password | CharField(128) | hashed | - |

**FK**: нет  
**Рекомендации**: добавить индекс на `role` при частых фильтрах по роли.

---

## CompanyProfile

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| user | OneToOneField(CustomUser) | CASCADE | - |
| company_name | CharField(255) | - | - |
| address | TextField | - | - |
| contact_phone | CharField(20) | - | - |
| contact_email | EmailField | - | - |
| inn | CharField(12) | blank | - |
| kpp | CharField(9) | blank | - |
| ogrn | CharField(15) | blank | - |

**FK**: user  
**Рекомендации**: индекс на `company_name` для поиска.

---

## InstitutionProfile

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| user | OneToOneField(CustomUser) | CASCADE | - |
| parent_company | FK(CompanyProfile) | CASCADE | - |
| institution_name | CharField(255) | - | - |
| institution_type | CharField(100) | - | - |
| email | EmailField | - | - |

**FK**: user, parent_company  
**Рекомендации**: индекс на `(parent_company_id, institution_type)` для фильтров.

---

## CollectionRequest

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| request_number | CharField(32) | unique, db_index | да |
| institution | FK(InstitutionProfile) | CASCADE | - |
| receiving_company | FK(CompanyProfile) | CASCADE | - |
| status | CharField(20) | choices | - |
| urgency | CharField(20) | choices | - |
| material_type | CharField(20) | choices | - |
| paper_weight_kg | DecimalField(10,2) | - | - |
| estimated_amount | DecimalField(10,2) | - | - |
| created_at | DateTimeField | auto_now_add | - |

**FK**: institution, receiving_company  
**Рекомендации**: индекс на `(receiving_company_id, status)`, `(created_at)` для сортировки.

---

## NewsArticle

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| title | CharField(200) | - | - |
| content | TextField | - | - |
| image | FileField | blank, null | - |
| created_at | DateTimeField | auto_now_add | - |
| is_published | BooleanField | default=True | - |
| author | FK(CustomUser) | SET_NULL, null | - |

**FK**: author  
**Рекомендации**: индекс на `(is_published, created_at)` для списка публичных статей.

---

## RequestMaterialLine

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| collection_request | FK(CollectionRequest) | CASCADE | - |
| material_type | CharField(20) | choices | - |
| amount_kg | DecimalField(10,2) | - | - |

**FK**: collection_request

---

## PriceList

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| material_type | CharField(20) | choices | - |
| price_per_kg | DecimalField(10,2) | - | - |
| valid_from | DateField | - | - |
| valid_to | DateField | null | - |
| is_active | BooleanField | default=True | - |

**FK**: нет  
**Рекомендации**: индекс на `(material_type, is_active, valid_from)`.

---

## InAppNotification

| Поле | Тип | Ограничения | Индексы |
|------|-----|-------------|---------|
| user | FK(CustomUser) | CASCADE | - |
| title | CharField(255) | - | - |
| read | BooleanField | default=False | - |
| created_at | DateTimeField | auto_now_add | - |

**FK**: user  
**Meta ordering**: `-created_at`

---

## Сводка

- Все модели имеют корректные FK и on_delete.
- `CollectionRequest.request_number` — db_index.
- Остальные индексы добавляются по мере нагрузки; текущая схема достаточна для MVP.
