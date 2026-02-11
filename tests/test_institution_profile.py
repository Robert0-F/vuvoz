"""
Tests for institution profile: institution can update contact_person and phone.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestInstitutionProfileUpdate:
    def test_institution_can_update_contact_person_and_phone(self, institution_client, institution_user):
        profile = institution_user.institution_profile
        url = reverse('institution-detail', args=[profile.id])
        payload = {
            'contact_person': 'Иванов Иван',
            'phone': '+7 999 123 45 67',
        }
        resp = institution_client.patch(url, payload, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['contact_person'] == 'Иванов Иван'
        assert '999' in resp.data['phone'] or resp.data['phone'] == '+7 999 123 45 67'
        profile.refresh_from_db()
        assert profile.contact_person == 'Иванов Иван'
