import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from collection.models import InstitutionProfile, SupportChatMessage, SupportConfig


User = get_user_model()


@pytest.fixture
def support_user(db):
    return User.objects.create_user(
        username='support@test.com',
        email='support@test.com',
        password='test123',
        role=User.Role.SUPPORT,
    )


@pytest.fixture
def support_client(support_user):
    client = APIClient()
    client.force_authenticate(user=support_user)
    return client


@pytest.mark.django_db
def test_support_can_access_assigned_institution_chat(support_user, support_client, institution_user):
    institution = institution_user.institution_profile
    institution.support_user = support_user
    institution.save(update_fields=['support_user'])

    list_resp = support_client.get('/api/support/institutions/')
    assert list_resp.status_code == 200
    assert len(list_resp.data) == 1
    assert list_resp.data[0]['id'] == institution.id

    create_resp = support_client.post(f'/api/support/chats/{institution.id}/', {'message': 'Здравствуйте'}, format='json')
    assert create_resp.status_code == 201
    assert create_resp.data['message'] == 'Здравствуйте'

    chat_resp = support_client.get(f'/api/support/chats/{institution.id}/')
    assert chat_resp.status_code == 200
    assert len(chat_resp.data) == 1
    assert chat_resp.data[0]['sender_role'] == 'support'


@pytest.mark.django_db
def test_support_cannot_access_unassigned_institution_chat(support_client, institution_user):
    institution = institution_user.institution_profile
    resp = support_client.get(f'/api/support/chats/{institution.id}/')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_institution_can_send_chat_message(support_user, institution_client, institution_user):
    institution = institution_user.institution_profile
    institution.support_user = support_user
    institution.save(update_fields=['support_user'])

    resp = institution_client.post(
        f'/api/support/chats/{institution.id}/',
        {'message': 'Нужна помощь'},
        format='json',
    )
    assert resp.status_code == 201
    assert resp.data['message'] == 'Нужна помощь'
    assert resp.data['is_mine'] is True


@pytest.mark.django_db
def test_institution_and_support_mark_messages_read(support_user, support_client, institution_client, institution_user):
    institution = institution_user.institution_profile
    institution.support_user = support_user
    institution.save(update_fields=['support_user'])

    create_by_inst = institution_client.post(
        f'/api/support/chats/{institution.id}/',
        {'message': 'Нужна помощь'},
        format='json',
    )
    assert create_by_inst.status_code == 201

    msg = SupportChatMessage.objects.get(pk=create_by_inst.data['id'])
    assert msg.is_read is False

    mark_read = support_client.post(f'/api/support/chats/{institution.id}/read/')
    assert mark_read.status_code == 200
    msg.refresh_from_db()
    assert msg.is_read is True


@pytest.mark.django_db
def test_support_config_assigns_all_institutions(admin_client, support_user, institution_user, company_user):
    second_user = User.objects.create_user(
        username='school02@test.com',
        email='school02@test.com',
        password='test123',
        role=User.Role.INSTITUTION,
    )
    second_inst = InstitutionProfile.objects.create(
        user=second_user,
        parent_company=company_user.company_profile,
        institution_name='Second School',
        address='789 School Rd',
        contact_person='Bob',
        phone='+1111111111',
        email='school02@test.com',
        institution_type='school',
    )
    assert institution_user.institution_profile.support_user_id is None
    assert second_inst.support_user_id is None

    config = SupportConfig.objects.create(support_user=support_user)
    assigned = config.assign_to_all_institutions()
    assert assigned == 2

    institution_user.institution_profile.refresh_from_db()
    second_inst.refresh_from_db()
    assert institution_user.institution_profile.support_user_id == support_user.id
    assert second_inst.support_user_id == support_user.id

    resp = admin_client.patch('/api/support-config/', {'support_user': support_user.id}, format='json')
    assert resp.status_code == 200
    assert resp.data['institutions_assigned'] == 2


@pytest.mark.django_db
def test_new_institution_gets_support_from_config(company_user, support_user):
    SupportConfig.objects.create(support_user=support_user)
    new_user = User.objects.create_user(
        username='newschool@test.com',
        email='newschool@test.com',
        password='test123',
        role=User.Role.INSTITUTION,
    )
    profile = InstitutionProfile.objects.create(
        user=new_user,
        parent_company=company_user.company_profile,
        institution_name='New School',
        address='1 New St',
        contact_person='Alice',
        phone='+2222222222',
        email='newschool@test.com',
        institution_type='school',
    )
    profile.refresh_from_db()
    assert profile.support_user_id == support_user.id


@pytest.mark.django_db
def test_unread_count_in_institutions_list(support_user, support_client, institution_client, institution_user):
    institution = institution_user.institution_profile
    institution.support_user = support_user
    institution.save(update_fields=['support_user'])

    institution_client.post(
        f'/api/support/chats/{institution.id}/',
        {'message': 'Помогите с заявкой'},
        format='json',
    )

    list_resp = support_client.get('/api/support/institutions/')
    assert list_resp.status_code == 200
    row = next(item for item in list_resp.data if item['id'] == institution.id)
    assert row['unread_count'] == 1
    assert row['last_message_preview']
    assert row['last_message_at']

