"""
Pytest configuration and fixtures for API tests.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from collection.models import CompanyProfile, InstitutionProfile, CollectionRequest

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company_user(db):
    user = User.objects.create_user(
        username='company@test.com',
        email='company@test.com',
        password='test123',
        role=User.Role.COMPANY,
    )
    CompanyProfile.objects.create(
        user=user,
        company_name='Test Company',
        address='123 Test St',
        contact_phone='+1234567890',
        contact_email='company@test.com',
    )
    return user


@pytest.fixture
def institution_user(company_user, db):
    inst_user = User.objects.create_user(
        username='institution@test.com',
        email='institution@test.com',
        password='test123',
        role=User.Role.INSTITUTION,
    )
    profile = InstitutionProfile.objects.create(
        user=inst_user,
        parent_company=company_user.company_profile,
        institution_name='Test Institution',
        address='456 School Rd',
        contact_person='Jane Doe',
        phone='+0987654321',
        email='institution@test.com',
        institution_type='school',
    )
    return inst_user


@pytest.fixture
def company_client(api_client, company_user):
    api_client.force_authenticate(user=company_user)
    return api_client


@pytest.fixture
def institution_client(api_client, institution_user):
    api_client.force_authenticate(user=institution_user)
    return api_client


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    user = User.objects.create_user(
        username='admin@test.com',
        email='admin@test.com',
        password='test123',
        is_staff=True,
        is_active=True,
    )
    user.role = 'admin'
    user.save(update_fields=['role'])
    return user


@pytest.fixture
def admin_client(admin_user):
    """Separate client for admin to avoid shared auth state with api_client."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
