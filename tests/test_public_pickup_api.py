"""Public materials catalog and pickup requests from homepage."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from collection.models import (
    Material,
    PriceList,
    PublicPickupRequest,
    PublicPickupRequestLine,
    RequestWeightLimit,
)


@pytest.fixture
def public_material(db):
    m, _ = Material.objects.get_or_create(
        code='cardboard',
        defaults={
            'name': 'Картон',
            'short_description': 'Гофрокартон',
            'icon': 'package-variant',
            'sort_order': 1,
            'is_active': True,
        },
    )
    PriceList.objects.get_or_create(
        material=m,
        defaults={'price_per_kg': Decimal('3.50'), 'is_active': True},
    )
    return m


@pytest.fixture
def public_material_plastic(db):
    m, _ = Material.objects.get_or_create(
        code='plastic',
        defaults={'name': 'Пластик', 'sort_order': 2, 'is_active': True},
    )
    PriceList.objects.get_or_create(
        material=m,
        defaults={'price_per_kg': Decimal('8.00'), 'is_active': True},
    )
    return m


@pytest.mark.django_db
class TestPublicMaterialsAPI:
    def test_list_materials_allow_any(self, api_client, public_material):
        url = '/api/public/materials/'
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]['code'] == 'cardboard'
        assert resp.data[0]['price_per_kg'] == '3.50'

    def test_weight_limits_public(self, api_client, weight_limits):
        weight_limits.min_kg = 50
        weight_limits.max_kg = 5000
        weight_limits.save()
        resp = api_client.get('/api/public/weight-limits/')
        assert resp.status_code == 200
        assert resp.data['min_kg'] == '50.00'


@pytest.mark.django_db
class TestPublicPickupAPI:
    def test_create_pickup_request_single_item(self, api_client, public_material, weight_limits):
        weight_limits.min_kg = 50
        weight_limits.max_kg = 5000
        weight_limits.save()
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        resp = api_client.post(
            '/api/public/pickup-requests/',
            {
                'items': [{'material_id': public_material.id, 'weight_kg': '100'}],
                'phone': '+79991234567',
                'address': 'г. Москва, ул. Тестовая, 1',
                'preferred_date': tomorrow,
                'contact_name': 'Иван',
            },
            format='json',
        )
        assert resp.status_code == 201
        assert PublicPickupRequest.objects.count() == 1
        row = PublicPickupRequest.objects.get()
        assert row.estimated_payout == Decimal('350.00')
        assert row.status == PublicPickupRequest.Status.NEW
        assert PublicPickupRequestLine.objects.filter(request=row).count() == 1

    def test_create_pickup_request_multi_items(self, api_client, public_material, public_material_plastic, weight_limits):
        weight_limits.min_kg = 50
        weight_limits.max_kg = 5000
        weight_limits.save()
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        resp = api_client.post(
            '/api/public/pickup-requests/',
            {
                'items': [
                    {'material_id': public_material.id, 'weight_kg': '100'},
                    {'material_id': public_material_plastic.id, 'weight_kg': '50'},
                ],
                'phone': '+79991234567',
                'address': 'Адрес',
                'preferred_date': tomorrow,
            },
            format='json',
        )
        assert resp.status_code == 201
        row = PublicPickupRequest.objects.get()
        assert row.estimated_payout == Decimal('750.00')  # 350 + 400
        assert len(resp.data['lines']) == 2
        assert 'Картон' in resp.data['materials_summary']

    def test_list_requires_admin(self, api_client, public_material, weight_limits):
        weight_limits.min_kg = 50
        weight_limits.max_kg = 5000
        weight_limits.save()
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        api_client.post(
            '/api/public/pickup-requests/',
            {
                'items': [{'material_id': public_material.id, 'weight_kg': '100'}],
                'phone': '+79991234567',
                'address': 'Адрес',
                'preferred_date': tomorrow,
            },
            format='json',
        )
        assert api_client.get('/api/public/pickup-requests/').status_code == 401

    def test_admin_lists_pickup(self, admin_client, public_material, weight_limits):
        weight_limits.min_kg = 50
        weight_limits.max_kg = 5000
        weight_limits.save()
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        api_client = APIClient()
        api_client.post(
            '/api/public/pickup-requests/',
            {
                'items': [{'material_id': public_material.id, 'weight_kg': '200'}],
                'phone': '+79990000000',
                'address': 'Адрес 2',
                'preferred_date': tomorrow,
            },
            format='json',
        )
        resp = admin_client.get('/api/public/pickup-requests/')
        assert resp.status_code == 200
        assert len(resp.data) >= 1
