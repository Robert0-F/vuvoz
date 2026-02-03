"""
Basic API tests for waste paper collection service.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthAPI:
    def test_token_obtain(self, api_client, company_user):
        url = reverse('token_obtain_pair')
        resp = api_client.post(url, {'username': 'company@test.com', 'password': 'test123'})
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_token_invalid(self, api_client):
        url = reverse('token_obtain_pair')
        resp = api_client.post(url, {'username': 'bad', 'password': 'bad'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeAPI:
    def test_me_company(self, company_client):
        url = reverse('current-user')
        resp = company_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['role'] == 'company'
        assert 'profile' in resp.data
        assert resp.data['profile']['company_name'] == 'Test Company'

    def test_me_institution(self, institution_client):
        url = reverse('current-user')
        resp = institution_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['role'] == 'institution'
        assert resp.data['profile']['institution_name'] == 'Test Institution'

    def test_me_unauthorized(self, api_client):
        url = reverse('current-user')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCompanyStats:
    def test_company_stats(self, company_client):
        url = reverse('stats-company')
        resp = company_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'total_institutions' in resp.data
        assert 'total_requests' in resp.data
        assert 'requests_by_status' in resp.data
        assert 'total_weight_kg' in resp.data
        assert 'recent_requests' in resp.data

    def test_company_stats_forbidden_for_institution(self, institution_client):
        url = reverse('stats-company')
        resp = institution_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestInstitutionStats:
    def test_institution_stats(self, institution_client):
        url = reverse('stats-institution')
        resp = institution_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'total_requests' in resp.data
        assert 'requests_by_status' in resp.data
        assert 'total_weight_all_time' in resp.data
        assert 'total_weight_this_month' in resp.data
