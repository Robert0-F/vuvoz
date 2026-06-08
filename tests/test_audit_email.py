import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status

from collection.models import AuditLog, InstitutionProfile, InstitutionRegistrationRequest


@pytest.mark.django_db
class TestEmailAndAudit:
    def test_registration_request_sends_email_and_audit(self, api_client, settings):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        url = reverse('registrationrequest-list')
        payload = {
            'first_name': 'Иван',
            'patronymic': 'Иванович',
            'institution_name': 'Школа N1',
            'address': 'ул. Тестовая, 1',
            'phone': '+79990000000',
            'email': 'lead@example.com',
        }
        resp = api_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert InstitutionRegistrationRequest.objects.filter(email='lead@example.com').exists()
        assert len(mail.outbox) == 1
        assert 'Заявка на регистрацию принята' in mail.outbox[0].subject
        assert mail.outbox[0].to == ['lead@example.com']
        assert AuditLog.objects.filter(
            action_type='create',
            target_model='InstitutionRegistrationRequest',
        ).exists()

    def test_reset_password_sends_email_and_audit(self, company_client, institution_user, settings):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        institution = InstitutionProfile.objects.get(user=institution_user)
        url = reverse('institution-reset-password', args=[institution.pk])
        resp = company_client.patch(url, {}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert 'new_password' in resp.data
        assert len(mail.outbox) == 1
        assert institution_user.email in mail.outbox[0].to
        assert AuditLog.objects.filter(
            action_type='reset_password',
            target_model='InstitutionProfile',
            target_id=str(institution.pk),
        ).exists()

    def test_news_create_writes_audit(self, admin_client, settings):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        url = reverse('news-list')
        payload = {'title': 'Audit test', 'content': 'content', 'is_published': True}
        resp = admin_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert AuditLog.objects.filter(
            action_type='create',
            target_model='NewsArticle',
        ).exists()

