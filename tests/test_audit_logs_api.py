import pytest
from django.urls import reverse
from rest_framework import status

from collection.models import AuditLog


@pytest.mark.django_db
class TestAuditLogsAPI:
    def test_admin_can_list_audit_logs(self, admin_client):
        AuditLog.objects.create(
            action_type='create',
            category=AuditLog.Category.INFO,
            short_summary='Created entity',
            target_model='CompanyProfile',
            target_id='1',
        )
        url = reverse('audit-logs')
        resp = admin_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'results' in resp.data
        assert resp.data['count'] >= 1

    def test_non_admin_cannot_list_audit_logs(self, company_client):
        url = reverse('audit-logs')
        resp = company_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_by_category(self, admin_client):
        AuditLog.objects.create(
            action_type='update',
            category=AuditLog.Category.WARNING,
            short_summary='Warning action',
            target_model='InstitutionProfile',
            target_id='10',
        )
        AuditLog.objects.create(
            action_type='status_change',
            category=AuditLog.Category.CRITICAL,
            short_summary='Critical action',
            target_model='CollectionRequest',
            target_id='33',
        )
        url = reverse('audit-logs')
        resp = admin_client.get(url, {'category': 'critical'})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1
        for row in resp.data['results']:
            assert row['category'] == 'critical'

    def test_export_csv(self, admin_client):
        AuditLog.objects.create(
            action_type='create',
            category=AuditLog.Category.INFO,
            short_summary='Export row',
            target_model='NewsArticle',
            target_id='99',
        )
        url = reverse('audit-logs-export')
        resp = admin_client.get(url, {'export_format': 'csv'})
        assert resp.status_code == status.HTTP_200_OK
        assert resp['Content-Type'].startswith('text/csv')
        body = resp.content.decode('utf-8')
        assert 'action_type' in body

    def test_database_info_admin_only(self, admin_client, company_client):
        url = reverse('database-info')
        resp_admin = admin_client.get(url)
        assert resp_admin.status_code == status.HTTP_200_OK
        assert 'db_type' in resp_admin.data
        assert 'engine' in resp_admin.data

        resp_company = company_client.get(url)
        assert resp_company.status_code == status.HTTP_403_FORBIDDEN
