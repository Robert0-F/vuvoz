#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate test data for the Statistics tab so each table shows meaningful data.

Creates collection requests with:
- Varied material types (paper, cardboard, newspapers, mixed, archive)
- Different institutions (for top organizations)
- Mix of statuses (new, accepted, completed)
- created_at spread over the last year (so period "1 year" shows data)
- completed_at set for completed requests, spread over recent months
- Some with material_lines, some with request-level material_type only

Run from project root (requires load_test_data.py to have been run for companies/institutions):
  python scripts/generate_stats_data.py

Or via Django shell:
  python manage.py shell -c "exec(open('scripts/generate_stats_data.py', encoding='utf-8').read()); run()"
"""
import os
import sys
from decimal import Decimal
from datetime import timedelta
import random

if __name__ == '__main__':
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_script_dir)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')
    import django
    django.setup()

from django.utils import timezone
from django.db.models import Count

from collection.models import (
    CompanyProfile,
    InstitutionProfile,
    CollectionRequest,
    RequestMaterialLine,
    PriceList,
)

MATERIAL_TYPES = ['paper', 'cardboard', 'newspapers', 'mixed', 'archive']


def run():
    companies = list(CompanyProfile.objects.all()[:2])
    institutions = list(InstitutionProfile.objects.select_related('parent_company').all())
    if not companies or not institutions:
        print("Сначала выполните scripts/load_test_data.py для создания компаний и организаций.")
        return

    # Ensure prices exist
    today = timezone.now().date()
    for mt in MATERIAL_TYPES:
        PriceList.objects.get_or_create(
            material_type=mt,
            valid_from=today,
            defaults={'price_per_kg': Decimal('5'), 'is_active': True},
        )

    now = timezone.now()
    created = 0

    # Create ~60 requests spread over the last 12 months
    for i in range(60):
        inst = random.choice(institutions)
        company = inst.parent_company

        # created_at: spread over last 365 days (more recent = more requests)
        days_ago = random.randint(0, 365)
        if i < 20:
            days_ago = random.randint(0, 30)
        elif i < 40:
            days_ago = random.randint(30, 180)
        created_at = now - timedelta(days=days_ago)

        # Status: ~50% completed, ~25% accepted, ~25% new
        r = random.random()
        if r < 0.5:
            status = CollectionRequest.Status.COMPLETED
        elif r < 0.75:
            status = CollectionRequest.Status.ACCEPTED
        else:
            status = CollectionRequest.Status.NEW

        # Material: single type or mixed (material_lines)
        use_lines = random.random() < 0.7
        if use_lines:
            mt1 = random.choice(MATERIAL_TYPES)
            mt2 = random.choice([m for m in MATERIAL_TYPES if m != mt1]) if random.random() < 0.4 else None
            kg1 = Decimal(str(random.randint(30, 200)))
            kg2 = Decimal(str(random.randint(20, 100))) if mt2 else Decimal('0')
            total_kg = kg1 + kg2
            material_type = 'mixed' if mt2 else mt1
        else:
            material_type = random.choice(MATERIAL_TYPES)
            total_kg = Decimal(str(random.randint(50, 250)))

        req = CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=status,
            material_type=material_type,
            paper_weight_kg=total_kg,
            estimated_amount=total_kg,
            comment=f'Тестовая заявка #{i+1} для статистики',
        )

        if use_lines:
            RequestMaterialLine.objects.create(
                collection_request=req,
                material_type=mt1,
                amount_kg=kg1,
            )
            if mt2 and kg2:
                RequestMaterialLine.objects.create(
                    collection_request=req,
                    material_type=mt2,
                    amount_kg=kg2,
                )
        req.save()

        # Override created_at
        CollectionRequest.objects.filter(pk=req.pk).update(created_at=created_at)

        if status == CollectionRequest.Status.COMPLETED:
            completed_at = created_at + timedelta(days=random.randint(0, min(14, days_ago)))
            CollectionRequest.objects.filter(pk=req.pk).update(
                completed_at=completed_at,
                actual_amount=total_kg,
                actual_value=req.estimated_value,
            )
        created += 1

    total = CollectionRequest.objects.count()
    by_status = CollectionRequest.objects.values('status').annotate(c=Count('id'))
    print(f"\nСоздано заявок для статистики: {created}")
    print(f"Всего заявок в БД: {total}")
    print("По статусам:")
    for row in by_status:
        print(f"  {row['status']}: {row['c']}")
    print("\nОткройте админку → Статистика → выберите период «1 год» и нажмите «Применить».")


if __name__ == '__main__':
    run()
