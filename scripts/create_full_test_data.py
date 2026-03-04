#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create full test dataset: 1 administrator, 8 companies, 80 institutions (Russian),
20 completed + 1 active request per institution. Completed requests have dates
spread over the last year for statistics and charts.

Institution types: school (школа), office (офис), manufacturing (производство),
private_client (частный клиент — в названии указывается ФИО).

Run from project root (UTF-8):
  python scripts/create_full_test_data.py
  python manage.py shell -c "exec(open('scripts/create_full_test_data.py', encoding='utf-8').read()); run()"

Before running: optionally wipe_db.py then run this, or run on empty DB.
"""
import os
import sys
import random
from decimal import Decimal
from datetime import timedelta

if __name__ == '__main__':
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_script_dir)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')
    import django
    django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from collection.models import (
    Material,
    PriceList,
    RequestWeightLimit,
    CompanyProfile,
    InstitutionProfile,
    CollectionRequest,
    RequestMaterialLine,
)

User = get_user_model()

# Пароль для всех тестовых пользователей
PASSWORD = 'test123'

# 1 администратор
ADMIN = {
    'username': 'admin@vuvoz.ru',
    'email': 'admin@vuvoz.ru',
    'first_name': 'Администратор',
    'last_name': 'Системы',
}

# 8 компаний (русские названия)
COMPANIES = [
    {'email': 'company1@test.com', 'name': 'ООО «Макулатура-Сервис»'},
    {'email': 'company2@test.com', 'name': 'Зелёный Вывоз'},
    {'email': 'company3@test.com', 'name': 'ЭкоТранс Переработка'},
    {'email': 'company4@test.com', 'name': 'Чистый Город'},
    {'email': 'company5@test.com', 'name': 'Бумажный Цикл'},
    {'email': 'company6@test.com', 'name': 'Вторсырьё Регион'},
    {'email': 'company7@test.com', 'name': 'Ресурс Макулатура'},
    {'email': 'company8@test.com', 'name': 'Сбор и Вывоз'},
]

# Типы организаций: школа, офис, производство, частный клиент (ФИО в названии)
INSTITUTION_TYPE_SCHOOL = 'school'
INSTITUTION_TYPE_OFFICE = 'office'
INSTITUTION_TYPE_MANUFACTURING = 'manufacturing'
INSTITUTION_TYPE_PRIVATE = 'private_client'

# 80 организаций: русские названия, смесь типов (школы, офисы, производство, частные клиенты с ФИО)
def _institutions():
    # Школы (20)
    schools = [
        ('school01@test.com', 'Средняя школа № 1 им. Пушкина'),
        ('school02@test.com', 'Гимназия № 2'),
        ('school03@test.com', 'Лицей «Солнечный»'),
        ('school04@test.com', 'Школа-интернат № 4'),
        ('school05@test.com', 'СОШ № 5 г. Москва'),
        ('school06@test.com', 'Гимназия имени Ломоносова'),
        ('school07@test.com', 'Школа № 7 с углублённым изучением'),
        ('school08@test.com', 'Лицей информационных технологий'),
        ('school09@test.com', 'Средняя школа № 9'),
        ('school10@test.com', 'Образовательный центр «Знание»'),
        ('school11@test.com', 'Школа № 11'),
        ('school12@test.com', 'Гимназия «Гармония»'),
        ('school13@test.com', 'СОШ № 13'),
        ('school14@test.com', 'Лицей № 14'),
        ('school15@test.com', 'Школа «Развитие»'),
        ('school16@test.com', 'Средняя школа № 16'),
        ('school17@test.com', 'Гимназия № 17'),
        ('school18@test.com', 'Школа-интернат «Надежда»'),
        ('school19@test.com', 'СОШ № 19'),
        ('school20@test.com', 'Лицей «Перспектива»'),
    ]
    # Офисы (20)
    offices = [
        ('office01@test.com', 'Офис «Северный»'),
        ('office02@test.com', 'Администрация города'),
        ('office03@test.com', 'Бизнес-центр «Парус»'),
        ('office04@test.com', 'Управление образования'),
        ('office05@test.com', 'Офис продаж «Рога и Копыта»'),
        ('office06@test.com', 'Деловой центр «Центральный»'),
        ('office07@test.com', 'Офис «Восток»'),
        ('office08@test.com', 'Администрация района'),
        ('office09@test.com', 'Офис «Запад»'),
        ('office10@test.com', 'Бизнес-парк «Сокол»'),
        ('office11@test.com', 'Офис «Юг»'),
        ('office12@test.com', 'Деловой дом «Москва»'),
        ('office13@test.com', 'Офис бухгалтерии № 1'),
        ('office14@test.com', 'Коворкинг «Рабочее место»'),
        ('office15@test.com', 'Офис «Полесье»'),
        ('office16@test.com', 'Администрация области'),
        ('office17@test.com', 'Офис «Нева»'),
        ('office18@test.com', 'Бизнес-центр «Арбат»'),
        ('office19@test.com', 'Офис «Сибирь»'),
        ('office20@test.com', 'Деловой центр «Урал»'),
    ]
    # Производство (20)
    manufacturing = [
        ('factory01@test.com', 'Завод «Упаковка»'),
        ('factory02@test.com', 'Типография «Печать»'),
        ('factory03@test.com', 'ЦБК Северный комбинат'),
        ('factory04@test.com', 'Производственный цех № 2'),
        ('factory05@test.com', 'Фабрика «Документы»'),
        ('factory06@test.com', 'ООО «Бумажный двор»'),
        ('factory07@test.com', 'Завод гофрокартона'),
        ('factory08@test.com', 'Типография «Книга»'),
        ('factory09@test.com', 'Цех переработки макулатуры'),
        ('factory10@test.com', 'Производство «Эко-пак»'),
        ('factory11@test.com', 'Завод «Картон»'),
        ('factory12@test.com', 'Типография «Оттиск»'),
        ('factory13@test.com', 'ООО «Вторбумага»'),
        ('factory14@test.com', 'Цех № 3 переработки'),
        ('factory15@test.com', 'Завод упаковочных материалов'),
        ('factory16@test.com', 'Типография «Спектр»'),
        ('factory17@test.com', 'Производство тары'),
        ('factory18@test.com', 'Завод «Гофро»'),
        ('factory19@test.com', 'Цех переработки № 1'),
        ('factory20@test.com', 'ООО «Бумага-Плюс»'),
    ]
    # Частные клиенты — в названии ФИО (20)
    private = [
        ('private01@test.com', 'Иванов Иван Иванович'),
        ('private02@test.com', 'Петрова Мария Сергеевна'),
        ('private03@test.com', 'Сидоров Пётр Александрович'),
        ('private04@test.com', 'Козлова Анна Владимировна'),
        ('private05@test.com', 'Новиков Дмитрий Николаевич'),
        ('private06@test.com', 'Морозова Елена Игоревна'),
        ('private07@test.com', 'Волков Андрей Сергеевич'),
        ('private08@test.com', 'Соколова Ольга Петровна'),
        ('private09@test.com', 'Лебедев Михаил Андреевич'),
        ('private10@test.com', 'Кузнецова Татьяна Викторовна'),
        ('private11@test.com', 'Попов Сергей Дмитриевич'),
        ('private12@test.com', 'Федорова Наталья Александровна'),
        ('private13@test.com', 'Михайлов Алексей Иванович'),
        ('private14@test.com', 'Васильева Светлана Олеговна'),
        ('private15@test.com', 'Андреев Игорь Владимирович'),
        ('private16@test.com', 'Павлова Юлия Сергеевна'),
        ('private17@test.com', 'Семёнов Роман Николаевич'),
        ('private18@test.com', 'Голубева Екатерина Петровна'),
        ('private19@test.com', 'Виноградов Николай Андреевич'),
        ('private20@test.com', 'Богданова Ирина Дмитриевна'),
    ]
    out = []
    for email, name in schools:
        out.append((email, name, INSTITUTION_TYPE_SCHOOL))
    for email, name in offices:
        out.append((email, name, INSTITUTION_TYPE_OFFICE))
    for email, name in manufacturing:
        out.append((email, name, INSTITUTION_TYPE_MANUFACTURING))
    for email, name in private:
        out.append((email, name, INSTITUTION_TYPE_PRIVATE))
    return out


def run():
    now = timezone.now()
    one_year_ago = now - timedelta(days=365)

    # 1. Материалы и цены
    for code, name in [('paper', 'Макулатура'), ('cardboard', 'Картон')]:
        mat, _ = Material.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True})
        PriceList.objects.get_or_create(
            material=mat,
            defaults={'price_per_kg': Decimal('5'), 'is_active': True},
        )
    RequestWeightLimit.objects.get_or_create(
        pk=1,
        defaults={'min_kg': Decimal('100'), 'max_kg': Decimal('100000')},
    )
    material_paper = Material.objects.get(code='paper')
    material_cardboard = Material.objects.get(code='cardboard')

    # 2. Администратор
    admin_user, created = User.objects.get_or_create(
        username=ADMIN['username'],
        defaults={
            'email': ADMIN['email'],
            'first_name': ADMIN['first_name'],
            'last_name': ADMIN['last_name'],
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )
    if created:
        admin_user.set_password(PASSWORD)
        admin_user.save()
        print(f"Создан администратор: {ADMIN['username']} / {PASSWORD}")

    # 3. Компании
    companies_profiles = []
    for c in COMPANIES:
        user, created = User.objects.get_or_create(
            username=c['email'],
            defaults={'email': c['email'], 'role': User.Role.COMPANY, 'is_active': True},
        )
        if created:
            user.set_password(PASSWORD)
            user.save()
        profile, _ = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': c['name'],
                'address': 'г. Москва, ул. Примерная, 1',
                'contact_phone': '+7 495 123 45 67',
                'contact_email': c['email'],
            },
        )
        if profile.company_name != c['name']:
            profile.company_name = c['name']
            profile.save()
        companies_profiles.append(profile)
    print(f"Компаний: {len(companies_profiles)}")

    # 4. Организации (80)
    institutions_data = _institutions()
    all_institutions = []
    for i, (email, name, inst_type) in enumerate(institutions_data):
        company = companies_profiles[i % len(companies_profiles)]
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'role': User.Role.INSTITUTION, 'is_active': True},
        )
        if created:
            user.set_password(PASSWORD)
            user.save()
        inst, _ = InstitutionProfile.objects.get_or_create(
            user=user,
            defaults={
                'parent_company': company,
                'institution_name': name,
                'address': f'г. Москва, ул. Организаций, {i + 1}',
                'contact_person': 'Ответственный',
                'phone': '+7 999 000 00 01',
                'email': email,
                'institution_type': inst_type,
            },
        )
        if inst.parent_company_id != company.id:
            inst.parent_company = company
            inst.save()
        if inst.institution_name != name:
            inst.institution_name = name
            inst.save()
        all_institutions.append(inst)
    print(f"Организаций: {len(all_institutions)}")

    # 5. Заявки: 20 завершённых + 1 активная на каждую организацию
    completed_count = 0
    active_count = 0
    for inst in all_institutions:
        company = inst.parent_company
        # 20 завершённых заявок — даты в пределах последнего года
        for j in range(20):
            days_ago_created = random.randint(5, 360)
            created_at = now - timedelta(days=days_ago_created)
            days_to_complete = random.randint(0, min(14, days_ago_created))
            completed_at = created_at + timedelta(days=days_to_complete)
            kg1 = Decimal(str(random.randint(30, 150)))
            kg2 = Decimal(str(random.randint(20, 100)))
            total_kg = kg1 + kg2
            req = CollectionRequest(
                institution=inst,
                receiving_company=company,
                status=CollectionRequest.Status.COMPLETED,
                paper_weight_kg=total_kg,
                estimated_amount=total_kg,
                actual_amount=total_kg,
                comment=f'Завершённая заявка от {inst.institution_name}',
            )
            req.save()
            RequestMaterialLine.objects.create(collection_request=req, material=material_paper, amount_kg=kg1)
            RequestMaterialLine.objects.create(collection_request=req, material=material_cardboard, amount_kg=kg2)
            req.save()
            req.refresh_from_db()
            actual_val = req.estimated_value
            CollectionRequest.objects.filter(pk=req.pk).update(
                created_at=created_at,
                completed_at=completed_at,
                actual_amount=total_kg,
                actual_value=actual_val,
                actual_collection_date=completed_at.date() if hasattr(completed_at, 'date') else completed_at,
            )
            completed_count += 1
        # 1 активная заявка (принятая)
        kg1 = Decimal(str(random.randint(40, 120)))
        kg2 = Decimal(str(random.randint(30, 80)))
        total_kg = kg1 + kg2
        req_active = CollectionRequest(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.ACCEPTED,
            paper_weight_kg=total_kg,
            estimated_amount=total_kg,
            comment=f'Активная заявка от {inst.institution_name}',
        )
        req_active.save()
        RequestMaterialLine.objects.create(collection_request=req_active, material=material_paper, amount_kg=kg1)
        RequestMaterialLine.objects.create(collection_request=req_active, material=material_cardboard, amount_kg=kg2)
        req_active.save()
        active_count += 1

    print(f"Заявок создано: {completed_count} завершённых, {active_count} активных")
    print("\nДоступ для входа:")
    print(f"  Администратор: {ADMIN['username']} / {PASSWORD}")
    print("  Компании: company1@test.com … company8@test.com /", PASSWORD)
    print("  Организации: school01@test.com, office01@test.com, factory01@test.com, private01@test.com … /", PASSWORD)


if __name__ == '__main__':
    run()
