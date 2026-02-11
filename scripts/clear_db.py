#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clear the database of all data except the admin user (and other superusers).
Removes: companies, institutions, requests, news, prices, weight limits, notifications.
Keeps: users with is_superuser=True (typically only admin).

Run from project root:
  python manage.py shell -c "exec(open('scripts/clear_db.py', encoding='utf-8').read()); run()"
Or:
  python scripts/clear_db.py
"""
import os
import sys

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
    RequestMaterialLine,
    InAppNotification,
    CollectionRequest,
    InstitutionProfile,
    CompanyProfile,
    NewsArticle,
    PriceList,
    RequestWeightLimit,
)

User = get_user_model()


def run():
    # Delete in order to respect foreign keys
    n_lines, _ = RequestMaterialLine.objects.all().delete()
    n_notif, _ = InAppNotification.objects.all().delete()
    n_req, _ = CollectionRequest.objects.all().delete()
    n_inst, _ = InstitutionProfile.objects.all().delete()
    n_comp, _ = CompanyProfile.objects.all().delete()
    n_news, _ = NewsArticle.objects.all().delete()
    n_price, _ = PriceList.objects.all().delete()
    n_lim, _ = RequestWeightLimit.objects.all().delete()
    # Keep only superusers (admin)
    non_admin = User.objects.filter(is_superuser=False)
    n_users = non_admin.count()
    non_admin.delete()

    print('База очищена (оставлен только админ):')
    print(f'  RequestMaterialLine: {n_lines}')
    print(f'  InAppNotification: {n_notif}')
    print(f'  CollectionRequest: {n_req}')
    print(f'  InstitutionProfile: {n_inst}')
    print(f'  CompanyProfile: {n_comp}')
    print(f'  NewsArticle: {n_news}')
    print(f'  PriceList: {n_price}')
    print(f'  RequestWeightLimit: {n_lim}')
    print(f'  Users (deleted): {n_users}')
    print('  Оставлены пользователи с is_superuser=True (админ).')


if __name__ == '__main__':
    run()
