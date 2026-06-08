#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create test data: 2 companies, 20 organizations (Russian names: schools, offices, stores, manufacturing),
with both completed and new requests.

Run from project root (use encoding=utf-8 so Russian text is correct):
  python manage.py shell -c "exec(open('scripts/load_test_data.py', encoding='utf-8').read()); run()"
Or run script directly (source must be saved as UTF-8):
  python scripts/load_test_data.py
"""
import os
import sys
from decimal import Decimal

# Allow running as script (add project root to path so "vuvoz" is found)
if __name__ == '__main__':
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_script_dir)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')
    import django
    django.setup()

from django.contrib.auth import get_user_model
from collection.models import (
    CompanyProfile,
    InstitutionProfile,
    CollectionRequest,
    RequestMaterialLine,
    RequestWeightLimit,
    Material,
    PriceList,
)

User = get_user_model()

# 2 companies
COMPANIES = [
    {'email': 'company1@test.com', 'name': 'ООО Макулатура-Сервис'},
    {'email': 'company2@test.com', 'name': 'Зелёный Вывоз'},
]

# 20 organizations: schools, offices, stores, manufacturing (Russian names)
ORGANIZATIONS = [
    # Schools (школы)
    {'email': 'school01@test.com', 'name': 'Средняя школа № 1', 'type': 'school'},
    {'email': 'school02@test.com', 'name': 'Гимназия имени Пушкина', 'type': 'school'},
    {'email': 'school03@test.com', 'name': 'Лицей № 15', 'type': 'school'},
    {'email': 'school04@test.com', 'name': 'Школа-интернат «Солнечный»', 'type': 'school'},
    # Offices (офисы)
    {'email': 'office01@test.com', 'name': 'Офис «Северный»', 'type': 'office'},
    {'email': 'office02@test.com', 'name': 'Администрация города', 'type': 'office'},
    {'email': 'office03@test.com', 'name': 'Бизнес-центр «Парус»', 'type': 'office'},
    {'email': 'office04@test.com', 'name': 'Офис продаж Рога и Копыта', 'type': 'office'},
    {'email': 'office05@test.com', 'name': 'Управление образования', 'type': 'office'},
    # Stores (магазины)
    {'email': 'store01@test.com', 'name': 'Магазин «Канцтовары»', 'type': 'store'},
    {'email': 'store02@test.com', 'name': 'Супермаркет «Продукты»', 'type': 'store'},
    {'email': 'store03@test.com', 'name': 'Торговый дом «Центральный»', 'type': 'store'},
    {'email': 'store04@test.com', 'name': 'Сеть магазинов «Бумага»', 'type': 'store'},
    # Manufacturing (производство)
    {'email': 'factory01@test.com', 'name': 'Завод «Упаковка»', 'type': 'manufacturing'},
    {'email': 'factory02@test.com', 'name': 'Типография «Печать»', 'type': 'manufacturing'},
    {'email': 'factory03@test.com', 'name': 'ЦБК Северный комбинат', 'type': 'manufacturing'},
    {'email': 'factory04@test.com', 'name': 'Производственный цех № 2', 'type': 'manufacturing'},
    {'email': 'factory05@test.com', 'name': 'Фабрика «Документы»', 'type': 'manufacturing'},
    {'email': 'factory06@test.com', 'name': 'ООО «Бумажный двор»', 'type': 'manufacturing'},
]

def run():
    from scripts.dev_env import get_dev_test_password

    password = get_dev_test_password()
    RequestWeightLimit.objects.get_or_create(
        pk=1,
        defaults={'min_kg': Decimal('100'), 'max_kg': Decimal('100000')},
    )
    # Ensure we have materials and prices for estimated_value
    from django.utils import timezone
    today = timezone.now().date()
    material_objs = {}
    for code, name in [
        ('paper', 'Бумага'),
        ('cardboard', 'Картон'),
        ('newspapers', 'Газеты'),
        ('mixed', 'Смешанная макулатура'),
        ('archive', 'Архивная бумага'),
    ]:
        material, _ = Material.objects.get_or_create(
            code=code,
            defaults={'name': name, 'is_active': True},
        )
        if not material.is_active:
            material.is_active = True
            material.save(update_fields=['is_active'])
        material_objs[code] = material
        PriceList.objects.get_or_create(
            material=material,
            defaults={
                'price_per_kg': Decimal('5'),
                'is_active': True,
                'valid_from': today,
            },
        )

    companies_profiles = []
    for c in COMPANIES:
        user, created = User.objects.get_or_create(
            username=c['email'],
            defaults={'email': c['email'], 'role': User.Role.COMPANY, 'is_active': True},
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Создана компания: {c['email']}")
        profile, _ = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': c['name'],
                'address': 'г. Москва, ул. Примерная, 1',
                'contact_phone': '+7 495 123 45 67',
                'contact_email': c['email'],
            },
        )
        if not profile.company_name == c['name']:
            profile.company_name = c['name']
            profile.save()
        companies_profiles.append(profile)

    all_institutions = []
    for i, org in enumerate(ORGANIZATIONS):
        company = companies_profiles[i % len(companies_profiles)]
        user, u_created = User.objects.get_or_create(
            username=org['email'],
            defaults={'email': org['email'], 'role': User.Role.INSTITUTION, 'is_active': True},
        )
        if u_created:
            user.set_password(password)
            user.save()
        inst, i_created = InstitutionProfile.objects.get_or_create(
            user=user,
            defaults={
                'parent_company': company,
                'institution_name': org['name'],
                'address': f'г. Москва, ул. Организаций, {i + 1}',
                'contact_person': 'Ответственный',
                'phone': '+7 999 000 00 01',
                'email': org['email'],
                'institution_type': org['type'],
            },
        )
        if inst.parent_company_id != company.id:
            inst.parent_company = company
            inst.save()
        all_institutions.append(inst)
        if i_created:
            print(f"  Организация: {org['name']} ({org['type']})")

    # Create requests: each org gets one NEW and one COMPLETED request (40 total)
    for idx, inst in enumerate(all_institutions):
        company = inst.parent_company
        kg1 = Decimal('50') + Decimal(str((idx * 7) % 100))
        kg2 = Decimal('30') + Decimal(str((idx * 3) % 50))
        total_kg = kg1 + kg2
        # New request
        req_new = CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.NEW,
            paper_weight_kg=total_kg,
            comment=f'Новая заявка от {inst.institution_name}',
        )
        RequestMaterialLine.objects.create(collection_request=req_new, material=material_objs['paper'], amount_kg=kg1)
        RequestMaterialLine.objects.create(collection_request=req_new, material=material_objs['cardboard'], amount_kg=kg2)
        req_new.save()
        # Completed request (with actual_amount/actual_value)
        req_done = CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.COMPLETED,
            paper_weight_kg=total_kg,
            comment=f'Завершённая заявка от {inst.institution_name}',
        )
        RequestMaterialLine.objects.create(collection_request=req_done, material=material_objs['paper'], amount_kg=kg1)
        RequestMaterialLine.objects.create(collection_request=req_done, material=material_objs['cardboard'], amount_kg=kg2)
        req_done.save()
        req_done.actual_amount = req_done.paper_weight_kg
        req_done.actual_value = req_done.estimated_value
        req_done.save(update_fields=['actual_amount', 'actual_value'])

    created_count = len(all_institutions) * 2
    print(f"\nСоздано заявок: {created_count} (по 1 новой и 1 завершённой на каждую организацию)")
    print("\nЛогины:")
    print("  Компания 1: company1@test.com / test123")
    print("  Компания 2: company2@test.com / test123")
    print("  Организации: school01@test.com … factory06@test.com / test123")


if __name__ == '__main__':
    run()
