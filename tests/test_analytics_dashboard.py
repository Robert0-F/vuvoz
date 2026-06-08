"""Tests for GET /api/analytics/dashboard/ (admin analytics)."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from collection.models import (
    CollectionRequest,
    Material,
    PublicPickupRequest,
    PublicPickupRequestLine,
)


@pytest.fixture
def analytics_material(db):
    material, _ = Material.objects.get_or_create(
        code='paper',
        defaults={'name': 'Бумага', 'is_active': True},
    )
    return material


@pytest.mark.django_db
class TestAdminAnalyticsDashboard:
    def test_requires_admin(self, company_client):
        url = reverse('analytics-dashboard')
        resp = company_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_core_blocks(self, admin_client):
        url = reverse('analytics-dashboard')
        resp = admin_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        for key in (
            'period', 'filters', 'kpis', 'materials', 'requests_insights', 'public_pickup',
        ):
            assert key in resp.data

    def test_requests_insights_funnel_and_backlog(
        self, admin_client, institution_user, analytics_material,
    ):
        inst = institution_user.institution_profile
        company = inst.parent_company
        now = timezone.now()
        CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.NEW,
            material_type='paper',
            paper_weight_kg=Decimal('100'),
            created_at=now,
        )
        CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.COMPLETED,
            material_type='paper',
            paper_weight_kg=Decimal('200'),
            created_at=now - timedelta(days=1),
            completed_at=now,
        )
        url = reverse('analytics-dashboard')
        resp = admin_client.get(url, {
            'date_from': (now.date() - timedelta(days=30)).isoformat(),
            'date_to': now.date().isoformat(),
            'basis': 'created',
        })
        assert resp.status_code == status.HTTP_200_OK
        insights = resp.data['requests_insights']
        assert 'funnel' in insights
        assert len(insights['funnel']) == 4
        assert insights['backlog']['new'] >= 1
        assert 'urgency_breakdown' in insights
        assert 'completion_time_buckets' in insights
        assert 'status_over_time' in insights

    def test_company_filter_scopes_kpis(self, admin_client, institution_user, analytics_material):
        inst = institution_user.institution_profile
        company = inst.parent_company
        now = timezone.now()
        CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.COMPLETED,
            material_type='paper',
            paper_weight_kg=Decimal('50'),
            created_at=now,
            completed_at=now,
        )
        url = reverse('analytics-dashboard')
        resp = admin_client.get(url, {
            'date_from': (now.date() - timedelta(days=7)).isoformat(),
            'date_to': now.date().isoformat(),
            'company_id': company.pk,
        })
        assert resp.status_code == status.HTTP_200_OK
        kpis = resp.data['kpis']
        assert kpis['is_entity_filtered'] is True
        assert kpis['total_companies'] == 1
        assert kpis['total_institutions'] >= 1
        assert resp.data['filters']['company_name'] == company.company_name

    def test_institution_filter(self, admin_client, institution_user, analytics_material):
        inst = institution_user.institution_profile
        company = inst.parent_company
        now = timezone.now()
        CollectionRequest.objects.create(
            institution=inst,
            receiving_company=company,
            status=CollectionRequest.Status.NEW,
            material_type='paper',
            paper_weight_kg=Decimal('30'),
            created_at=now,
        )
        url = reverse('analytics-dashboard')
        resp = admin_client.get(url, {
            'date_from': (now.date() - timedelta(days=7)).isoformat(),
            'date_to': now.date().isoformat(),
            'institution_id': inst.pk,
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['kpis']['is_entity_filtered'] is True
        assert resp.data['kpis']['total_institutions'] == 1
        assert resp.data['filters']['institution_name'] == inst.institution_name

    def test_public_pickup_block(self, admin_client, analytics_material):
        now = timezone.now()
        pickup = PublicPickupRequest.objects.create(
            phone='+79990001122',
            address='ул. Тестовая, 1',
            preferred_date=now.date(),
            estimated_payout=Decimal('500'),
            status=PublicPickupRequest.Status.NEW,
        )
        PublicPickupRequestLine.objects.create(
            request=pickup,
            material=analytics_material,
            weight_kg=Decimal('25'),
            line_payout=Decimal('500'),
        )
        url = reverse('analytics-dashboard')
        resp = admin_client.get(url, {
            'date_from': (now.date() - timedelta(days=1)).isoformat(),
            'date_to': (now.date() + timedelta(days=1)).isoformat(),
        })
        assert resp.status_code == status.HTTP_200_OK
        pp = resp.data['public_pickup']
        assert pp['kpis']['total_period'] >= 1
        assert pp['kpis']['total_kg'] >= 25
        assert len(pp['by_status']) >= 1
        assert len(pp['materials']) >= 1
