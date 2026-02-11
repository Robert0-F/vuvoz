"""
Tests for weight limits API and request validation (min/max kg).
"""
import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status

from collection.models import RequestWeightLimit, RequestMaterialLine


@pytest.mark.django_db
class TestWeightLimitsAPI:
    def test_weight_limits_authenticated(self, institution_client):
        url = reverse('weight-limits')
        resp = institution_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'min_kg' in resp.data
        assert 'max_kg' in resp.data
        assert Decimal(resp.data['min_kg']) >= 0
        assert Decimal(resp.data['max_kg']) >= Decimal(resp.data['min_kg'])

    def test_weight_limits_unauthorized(self, api_client):
        url = reverse('weight-limits')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRequestWeightValidation:
    """Create request with material_lines: total must be between min_kg and max_kg."""

    def test_create_request_below_min_rejected(self, institution_client, weight_limits):
        weight_limits.min_kg = Decimal('100')
        weight_limits.save()
        url = reverse('collectionrequest-list')
        payload = {
            'material_lines': [
                {'material_type': 'paper', 'amount_kg': '50'},
            ],
            'comment': '',
        }
        resp = institution_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'material_lines' in resp.data or 'Суммарный' in str(resp.data)

    def test_create_request_above_max_rejected(self, institution_client, weight_limits):
        weight_limits.max_kg = Decimal('500')
        weight_limits.save()
        url = reverse('collectionrequest-list')
        payload = {
            'material_lines': [
                {'material_type': 'paper', 'amount_kg': '300'},
                {'material_type': 'cardboard', 'amount_kg': '300'},
            ],
            'comment': '',
        }
        resp = institution_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_request_within_range_accepted(self, institution_client, weight_limits):
        weight_limits.min_kg = Decimal('100')
        weight_limits.max_kg = Decimal('100000')
        weight_limits.save()
        url = reverse('collectionrequest-list')
        payload = {
            'material_lines': [
                {'material_type': 'paper', 'amount_kg': '60'},
                {'material_type': 'cardboard', 'amount_kg': '50'},
            ],
            'comment': 'Test',
        }
        resp = institution_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data.get('request_number') or resp.data.get('id')
        assert len(resp.data.get('material_lines', [])) == 2
