#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Delete ALL data from the database (including all users and admin).
Use this when you need a completely empty database (e.g. before loading fresh test data).

Recommended: create a backup first: python scripts/backup_db.py

Run from project root:
  python scripts/wipe_db.py
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
    PointsOrderLine,
    PointsOrder,
    InstitutionBonus,
    RequestMaterialLine,
    InAppNotification,
    CollectionRequest,
    InstitutionProfile,
    CompanyProfile,
    NewsArticle,
    PriceList,
    RequestWeightLimit,
    Product,
    BonusConfig,
    Material,
    InstitutionRegistrationRequest,
)

User = get_user_model()


def run():
    # Delete in dependency order (children first)
    n_pol, _ = PointsOrderLine.objects.all().delete()
    n_po, _ = PointsOrder.objects.all().delete()
    n_ib, _ = InstitutionBonus.objects.all().delete()
    n_rml, _ = RequestMaterialLine.objects.all().delete()
    n_notif, _ = InAppNotification.objects.all().delete()
    n_req, _ = CollectionRequest.objects.all().delete()
    n_inst, _ = InstitutionProfile.objects.all().delete()
    n_comp, _ = CompanyProfile.objects.all().delete()
    n_news, _ = NewsArticle.objects.all().delete()
    n_price, _ = PriceList.objects.all().delete()
    n_lim, _ = RequestWeightLimit.objects.all().delete()
    n_prod, _ = Product.objects.all().delete()
    n_bonus_cfg, _ = BonusConfig.objects.all().delete()
    n_mat, _ = Material.objects.all().delete()
    n_reg, _ = InstitutionRegistrationRequest.objects.all().delete()
    n_users, _ = User.objects.all().delete()

    print('База данных полностью очищена:')
    print(f'  PointsOrderLine: {n_pol}')
    print(f'  PointsOrder: {n_po}')
    print(f'  InstitutionBonus: {n_ib}')
    print(f'  RequestMaterialLine: {n_rml}')
    print(f'  InAppNotification: {n_notif}')
    print(f'  CollectionRequest: {n_req}')
    print(f'  InstitutionProfile: {n_inst}')
    print(f'  CompanyProfile: {n_comp}')
    print(f'  NewsArticle: {n_news}')
    print(f'  PriceList: {n_price}')
    print(f'  RequestWeightLimit: {n_lim}')
    print(f'  Product: {n_prod}')
    print(f'  BonusConfig: {n_bonus_cfg}')
    print(f'  Material: {n_mat}')
    print(f'  InstitutionRegistrationRequest: {n_reg}')
    print(f'  User: {n_users}')


if __name__ == '__main__':
    run()
