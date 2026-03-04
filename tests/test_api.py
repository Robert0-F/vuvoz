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


@pytest.mark.django_db
class TestAdminRole:
    """Verify admin user has correct role for permission checks."""

    def test_admin_me_returns_role(self, admin_client):
        url = reverse('current-user')
        resp = admin_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data.get('role') == 'admin'

    def test_admin_can_create_price(self, admin_client):
        """IsAdministrator allows admin to create PriceList (admin-only resource)."""
        from collection.models import Material, PriceList
        from django.utils import timezone
        # Use a dedicated material so we don't conflict with existing PriceList for 'paper'
        material = Material.objects.create(
            code='test_material_price',
            name='Тестовый материал',
            is_active=True,
        )
        # Ensure no price exists for this material (clean state)
        PriceList.objects.filter(material=material).delete()
        url = reverse('pricelist-list')
        data = {
            'material': material.pk,
            'price_per_kg': '5.00',
            'valid_from': timezone.now().date().isoformat(),
        }
        resp = admin_client.post(url, data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestNewsAPI:
    """News API: public GET list/retrieve; admin-only POST/PUT/DELETE."""

    def test_news_list_public(self, api_client):
        """GET /api/news/ - no auth required, returns published only."""
        from collection.models import NewsArticle
        NewsArticle.objects.create(title='Pub', content='Content', is_published=True)
        NewsArticle.objects.create(title='Unpub', content='Hidden', is_published=False)
        url = reverse('news-list')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get('results', resp.data) if isinstance(resp.data, dict) else resp.data
        assert len(results) == 1
        assert results[0]['title'] == 'Pub'

    def test_news_retrieve_public(self, api_client):
        """GET /api/news/{id}/ - no auth required for published article."""
        from collection.models import NewsArticle
        art = NewsArticle.objects.create(title='Test', content='Body', is_published=True)
        url = reverse('news-detail', args=[art.pk])
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['title'] == 'Test'
        assert resp.data['content'] == 'Body'

    def test_news_retrieve_unpublished_404_for_anon(self, api_client):
        """Unpublished article returns 404 for anonymous users."""
        from collection.models import NewsArticle
        art = NewsArticle.objects.create(title='Secret', content='Hidden', is_published=False)
        url = reverse('news-detail', args=[art.pk])
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_news_create_admin_only(self, admin_client, company_client):
        """POST /api/news/ - only admin can create."""
        from collection.models import NewsArticle
        from rest_framework.test import APIClient
        url = reverse('news-list')
        data = {'title': 'New Article', 'content': 'Full content here', 'is_published': True}
        anon = APIClient()
        resp = anon.post(url, data, format='json')
        assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        resp = company_client.post(url, data, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        resp = admin_client.post(url, data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert NewsArticle.objects.filter(title='New Article').exists()

    def test_news_delete_admin_only(self, admin_client, company_client):
        """DELETE /api/news/{id}/ - only admin can delete."""
        from collection.models import NewsArticle
        art = NewsArticle.objects.create(title='To Delete', content='x', is_published=True)
        url = reverse('news-detail', args=[art.pk])
        resp = company_client.delete(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        resp = admin_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not NewsArticle.objects.filter(pk=art.pk).exists()
