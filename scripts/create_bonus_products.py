#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create 10 test bonus products (for green points catalog).
Run from project root: python scripts/create_bonus_products.py
"""
import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')

import django
django.setup()

from decimal import Decimal
from collection.models import Product

PRODUCTS = [
    {
        'name': 'Набор канцтоваров и инструментов',
        'description': 'Ручки шариковые (5 шт.), тетради 48 листов (10 шт.), карандаши, ластики, линейка, ножницы, степлер, скрепки, клей-карандаш, отвёртки, пассатижи.',
        'price_in_points': Decimal('150'),
    },
    {
        'name': 'Набор ручек и маркеров',
        'description': 'Шариковые ручки синие и чёрные (10 шт.), маркеры для досок (4 шт.), маркеры текстовые (5 шт.).',
        'price_in_points': Decimal('80'),
    },
    {
        'name': 'Тетради и блокноты',
        'description': 'Тетради 96 листов (5 шт.), блокноты А5 (3 шт.), блокноты А4 (2 шт.).',
        'price_in_points': Decimal('120'),
    },
    {
        'name': 'Папки и файлы',
        'description': 'Папки-регистраторы (3 шт.), файлы А4 (2 упаковки по 100 шт.), скоросшиватели (5 шт.).',
        'price_in_points': Decimal('100'),
    },
    {
        'name': 'Набор для черчения',
        'description': 'Линейки, угольники, транспортир, циркуль, карандаши разной твёрдости, ластик для черчения.',
        'price_in_points': Decimal('200'),
    },
    {
        'name': 'Канцелярские мелочи',
        'description': 'Скрепки, кнопки, стикеры, клей ПВА, клей-карандаш, корректор, дырокол, степлер и скобы.',
        'price_in_points': Decimal('60'),
    },
    {
        'name': 'Набор отвёрток',
        'description': 'Отвёртки крестовые и плоские разного размера (6 шт.), удобные рукоятки.',
        'price_in_points': Decimal('180'),
    },
    {
        'name': 'Инструменты для офиса',
        'description': 'Пассатижи, кусачки, ножницы по металлу, рулетка 3 м, нож канцелярский с лезвиями.',
        'price_in_points': Decimal('220'),
    },
    {
        'name': 'Бумага для принтера',
        'description': 'Пачка офисной бумаги А4 500 листов, плотность 80 г/м².',
        'price_in_points': Decimal('250'),
    },
    {
        'name': 'Органайзер на стол',
        'description': 'Настольный органайзер с отделениями для ручек, скрепок, визиток и документов.',
        'price_in_points': Decimal('90'),
    },
]


def run():
    created = 0
    for p in PRODUCTS:
        obj, c = Product.objects.get_or_create(
            name=p['name'],
            defaults={
                'description': p['description'],
                'price_in_points': p['price_in_points'],
                'is_active': True,
            },
        )
        if c:
            created += 1
            print(f"  Создан: {obj.name} — {obj.price_in_points} баллов")
    print(f"\nГотово. Создано новых товаров: {created}, всего в каталоге: {Product.objects.count()}")


if __name__ == '__main__':
    run()
