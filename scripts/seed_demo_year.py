#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Демо-данные для тестового сервера: 2 компании, 12 учреждений, заявки за ~1 год.

Перед запуском: очистите БД (см. README_SETUP.md) и создайте суперпользователя.

Запуск (локально, DJANGO_DEBUG=True):
  python scripts/seed_demo_year.py

Запуск на production-сервере (только для тестовой демо-БД):
  DEMO_SEED_ALLOW_PRODUCTION=1 python scripts/seed_demo_year.py

Или через Django shell:
  python manage.py shell -c "exec(open('scripts/seed_demo_year.py', encoding='utf-8').read()); run()"
"""
import os
import sys
from datetime import timedelta
from decimal import Decimal
import random

if __name__ == '__main__':
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_script_dir)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')
    import django

    django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from collection.models import (
    BonusConfig,
    CompanyProfile,
    CollectionRequest,
    InstitutionProfile,
    Material,
    PriceList,
    RequestMaterialLine,
    RequestWeightLimit,
)

User = get_user_model()

PASSWORD = 'test123'

# Все 9 типов материалов: code, название, цена руб/кг (10–20)
MATERIALS = [
    ('archive', 'Архивная бумага', Decimal('12')),
    ('newspapers', 'Газеты', Decimal('14')),
    ('canisters', 'Канистры/флаконы', Decimal('18')),
    ('cardboard', 'Картон', Decimal('11')),
    ('paper', 'Макулатура', Decimal('15')),
    ('metal', 'Металл бытовой', Decimal('20')),
    ('polyethylene', 'Полиэтилен/стрейч пленка', Decimal('16')),
    ('mixed', 'Смешанная макулатура', Decimal('10')),
    ('glass', 'Стекло (бутылки)', Decimal('13')),
]

COMPANIES = [
    {
        'email': 'company1@test.com',
        'name': 'ООО «Зелёный Вывоз»',
        'address': 'г. Москва, ул. Экологическая, 10',
        'phone': '+7 495 111-22-33',
    },
    {
        'email': 'company2@test.com',
        'name': 'ООО «ЭкоСбор Москва»',
        'address': 'г. Москва, пр-т Мира, 45',
        'phone': '+7 495 444-55-66',
    },
]

# 12 учреждений: по 6 на каждую компанию (company_index 0 или 1)
INSTITUTIONS = [
    {'email': 'school01@test.com', 'name': 'Средняя школа № 7', 'type': 'school', 'company_index': 0},
    {'email': 'school02@test.com', 'name': 'Гимназия «Север»', 'type': 'school', 'company_index': 0},
    {'email': 'office01@test.com', 'name': 'Бизнес-центр «Горизонт»', 'type': 'office', 'company_index': 0},
    {'email': 'office02@test.com', 'name': 'Администрация Северного района', 'type': 'office', 'company_index': 0},
    {'email': 'store01@test.com', 'name': 'Магазин «ЭкоМаркет»', 'type': 'store', 'company_index': 0},
    {'email': 'factory01@test.com', 'name': 'Типография «Печатный двор»', 'type': 'manufacturing', 'company_index': 0},
    {'email': 'school03@test.com', 'name': 'Лицей № 22', 'type': 'school', 'company_index': 1},
    {'email': 'school04@test.com', 'name': 'Школа-интернат «Рассвет»', 'type': 'school', 'company_index': 1},
    {'email': 'office03@test.com', 'name': 'Офис «Технопарк»', 'type': 'office', 'company_index': 1},
    {'email': 'store02@test.com', 'name': 'ТЦ «Северный»', 'type': 'store', 'company_index': 1},
    {'email': 'store03@test.com', 'name': 'Сеть «КанцМарт»', 'type': 'store', 'company_index': 1},
    {'email': 'factory02@test.com', 'name': 'Завод «Упаковка Плюс»', 'type': 'manufacturing', 'company_index': 1},
]


def _get_password():
    """Демо-пароль test123; на production нужен явный флаг DEMO_SEED_ALLOW_PRODUCTION=1."""
    if os.environ.get('DEMO_SEED_ALLOW_PRODUCTION') == '1':
        return os.environ.get('DEMO_SEED_PASSWORD', PASSWORD)
    try:
        from django.conf import settings

        if not settings.DEBUG:
            raise RuntimeError('production')
    except RuntimeError:
        raise RuntimeError(
            'На сервере задайте DEMO_SEED_ALLOW_PRODUCTION=1 (см. README_SETUP.md).'
        ) from None
    return os.environ.get('DEMO_SEED_PASSWORD', PASSWORD)


def _ensure_catalog():
    """Материалы, прайс 10–20 руб/кг, лимиты веса, бонусы."""
    today = timezone.now().date()
    material_objs = {}
    for sort_order, (code, name, price) in enumerate(MATERIALS):
        material, _ = Material.objects.update_or_create(
            code=code,
            defaults={'name': name, 'is_active': True, 'sort_order': sort_order},
        )
        material_objs[code] = material
        PriceList.objects.update_or_create(
            material=material,
            defaults={
                'price_per_kg': price,
                'is_active': True,
                'valid_from': today - timedelta(days=400),
            },
        )
    RequestWeightLimit.objects.update_or_create(
        pk=1,
        defaults={'min_kg': Decimal('100'), 'max_kg': Decimal('100000')},
    )
    if not BonusConfig.objects.exists():
        BonusConfig.objects.create(bonus_percent=Decimal('5'))
    else:
        BonusConfig.objects.update(bonus_percent=Decimal('5'))
    return material_objs


def _create_user(email, role):
    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email, 'role': role, 'is_active': True},
    )
    if created or not user.check_password(_get_password()):
        user.set_password(_get_password())
        user.role = role
        user.is_active = True
        user.save()
    return user


def _create_companies():
    profiles = []
    for c in COMPANIES:
        user = _create_user(c['email'], User.Role.COMPANY)
        profile, _ = CompanyProfile.objects.update_or_create(
            user=user,
            defaults={
                'company_name': c['name'],
                'address': c['address'],
                'contact_phone': c['phone'],
                'contact_email': c['email'],
            },
        )
        profiles.append(profile)
        print(f'  Компания: {c["name"]} ({c["email"]})')
    return profiles


def _create_institutions(company_profiles):
    institutions = []
    for i, data in enumerate(INSTITUTIONS):
        company = company_profiles[data['company_index']]
        user = _create_user(data['email'], User.Role.INSTITUTION)
        inst, _ = InstitutionProfile.objects.update_or_create(
            user=user,
            defaults={
                'parent_company': company,
                'institution_name': data['name'],
                'address': f'г. Москва, ул. Организаций, {i + 1}',
                'contact_person': 'Ответственный за вторсырьё',
                'phone': f'+7 999 {100 + i:03d} {10 + i:02d} {20 + i:02d}',
                'email': data['email'],
                'institution_type': data['type'],
            },
        )
        if inst.parent_company_id != company.id:
            inst.parent_company = company
            inst.save(update_fields=['parent_company'])
        institutions.append(inst)
        print(f'  Учреждение: {data["name"]} -> {company.company_name}')
    return institutions


def _weights_for_all_materials(inst_index):
    """9 позиций, суммарно ≥ 100 кг."""
    base = [
        Decimal('15'), Decimal('12'), Decimal('10'), Decimal('18'), Decimal('14'),
        Decimal('11'), Decimal('13'), Decimal('16'), Decimal('12'),
    ]
    return [w + Decimal(str((inst_index + i) % 5)) for i, w in enumerate(base)]


def _create_completed_request(inst, company, material_objs, line_specs, created_at, comment):
    """
    line_specs: list of (material_code, amount_kg)
    """
    completed_at = created_at + timedelta(days=random.randint(1, 10))
    collection_date = completed_at.date()

    req = CollectionRequest(
        institution=inst,
        receiving_company=company,
        status=CollectionRequest.Status.COMPLETED,
        comment=comment,
        desired_date=created_at.date() + timedelta(days=3),
        estimated_collection_date=collection_date,
        actual_collection_date=collection_date,
        completed_at=completed_at,
    )
    req.save()

    for code, kg in line_specs:
        RequestMaterialLine.objects.create(
            collection_request=req,
            material=material_objs[code],
            amount_kg=kg,
        )
    req.save()
    req.actual_amount = req.paper_weight_kg
    req.actual_value = req.estimated_value
    req.save(update_fields=['actual_amount', 'actual_value'])

    CollectionRequest.objects.filter(pk=req.pk).update(created_at=created_at)
    return req


def _create_active_request(inst, company, material_objs, status, line_specs, created_at, comment):
    req = CollectionRequest(
        institution=inst,
        receiving_company=company,
        status=status,
        comment=comment,
        desired_date=timezone.now().date() + timedelta(days=7),
    )
    req.save()
    for code, kg in line_specs:
        RequestMaterialLine.objects.create(
            collection_request=req,
            material=material_objs[code],
            amount_kg=kg,
        )
    req.save()
    CollectionRequest.objects.filter(pk=req.pk).update(created_at=created_at)
    return req


def _seed_requests(institutions, material_objs):
    random.seed(42)
    now = timezone.now()
    codes = [c[0] for c in MATERIALS]
    completed_count = 0
    active_count = 0

    for idx, inst in enumerate(institutions):
        company = inst.parent_company

        # 1) Завершённая заявка со всеми 9 материалами (разные месяцы года)
        month_offset = idx % 12
        created_full = now - timedelta(days=330 - month_offset * 28)
        weights = _weights_for_all_materials(idx)
        line_specs_full = list(zip(codes, weights))
        _create_completed_request(
            inst,
            company,
            material_objs,
            line_specs_full,
            created_full,
            f'Полный вывоз всех видов вторсырья — {inst.institution_name}',
        )
        completed_count += 1

        # 2) Ещё 2–3 завершённые заявки в течение года (часть материалов)
        for j in range(2 + (idx % 2)):
            days_ago = random.randint(30, 360)
            created_at = now - timedelta(days=days_ago)
            n_lines = random.randint(2, 5)
            picked = random.sample(codes, n_lines)
            line_specs = [
                (code, Decimal(str(random.randint(25, 80))))
                for code in picked
            ]
            total = sum(kg for _, kg in line_specs)
            if total < Decimal('100'):
                line_specs[0] = (line_specs[0][0], line_specs[0][1] + (Decimal('100') - total))
            _create_completed_request(
                inst,
                company,
                material_objs,
                line_specs,
                created_at,
                f'Регулярный вывоз #{j + 1} — {inst.institution_name}',
            )
            completed_count += 1

        # 3) Текущая заявка (новая или принятая)
        if idx % 3 == 0:
            status = CollectionRequest.Status.NEW
        else:
            status = CollectionRequest.Status.ACCEPTED
        picked = random.sample(codes, 3)
        line_specs = [(code, Decimal(str(random.randint(40, 70)))) for code in picked]
        total = sum(kg for _, kg in line_specs)
        if total < Decimal('100'):
            line_specs[-1] = (line_specs[-1][0], line_specs[-1][1] + (Decimal('100') - total))
        _create_active_request(
            inst,
            company,
            material_objs,
            status,
            line_specs,
            now - timedelta(days=random.randint(1, 14)),
            f'Текущая заявка — {inst.institution_name}',
        )
        active_count += 1

    return completed_count, active_count


def run():
    if User.objects.filter(role=User.Role.ADMIN).exists():
        print('Внимание: в БД уже есть администратор(ы). Скрипт не создаёт admin — используйте createsuperuser.')
    elif not User.objects.filter(is_superuser=True).exists():
        print('Внимание: суперпользователь не найден. Рекомендуется: python manage.py createsuperuser')

    existing = CollectionRequest.objects.count()
    if existing > 0:
        print(f'В БД уже есть {existing} заявок. Для чистого демо сначала выполните flush (README_SETUP.md).')
        answer = os.environ.get('DEMO_SEED_FORCE', '')
        if answer != '1':
            print('Прервать. Для добавления к существующим данным: DEMO_SEED_FORCE=1')
            return

    print('Каталог материалов и цены (10–20 руб/кг)...')
    material_objs = _ensure_catalog()

    print('Компании...')
    companies = _create_companies()

    print('Учреждения (12)...')
    institutions = _create_institutions(companies)

    print('Заявки за ~1 год...')
    completed, active = _seed_requests(institutions, material_objs)

    print()
    print('=' * 60)
    print(f'Готово: {len(companies)} компании, {len(institutions)} учреждений')
    print(f'  Завершённых заявок: {completed}')
    print(f'  Активных (новая/принята): {active}')
    print(f'  Материалов в каталоге: {len(MATERIALS)}')
    print(f'  Пароль всех тестовых пользователей: {_get_password()}')
    print('  Полный список логинов: docs/DEMO_USERS.md')
    print('=' * 60)


if __name__ == '__main__':
    run()
