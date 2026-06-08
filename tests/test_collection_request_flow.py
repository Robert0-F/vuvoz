"""Collection request accept → complete → institution confirm flow."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from collection.models import CollectionRequest


@pytest.fixture
def collection_request(institution_user, weight_limits):
    weight_limits.min_kg = 100
    weight_limits.max_kg = 100000
    weight_limits.save()
    client = APIClient()
    client.force_authenticate(user=institution_user)
    url = reverse('collectionrequest-list')
    resp = client.post(
        url,
        {
            'material_lines': [{'material_type': 'paper', 'amount_kg': '150'}],
            'desired_date': '2026-06-15',
            'comment': 'Test request',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED
    return CollectionRequest.objects.get(pk=resp.data['id'])


@pytest.mark.django_db
def test_company_accept_sets_pickup_date(company_client, collection_request):
    url = reverse('collectionrequest-detail', args=[collection_request.pk])
    resp = company_client.patch(
        url,
        {
            'status': 'accepted',
            'actual_collection_date': '2026-06-20',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['status'] == 'accepted'
    assert resp.data['actual_collection_date'] == '2026-06-20'

    collection_request.refresh_from_db()
    assert collection_request.status == CollectionRequest.Status.ACCEPTED


@pytest.mark.django_db
def test_company_complete_waits_for_institution_confirmation(
    company_client, collection_request,
):
    company_client.patch(
        reverse('collectionrequest-detail', args=[collection_request.pk]),
        {'status': 'accepted', 'actual_collection_date': '2026-06-20'},
        format='json',
    )

    complete_url = reverse('collectionrequest-complete', args=[collection_request.pk])
    resp = company_client.post(
        complete_url,
        {'actual_amount': '140', 'actual_collection_date': '2026-06-20'},
        format='json',
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['status'] == 'pending_confirmation'
    assert resp.data['actual_amount'] == '140.00'

    collection_request.refresh_from_db()
    assert collection_request.status == CollectionRequest.Status.PENDING_CONFIRMATION
    assert collection_request.completed_at is None


@pytest.mark.django_db
def test_institution_confirms_completion(
    company_client, institution_user, collection_request,
):
    company_client.patch(
        reverse('collectionrequest-detail', args=[collection_request.pk]),
        {'status': 'accepted'},
        format='json',
    )
    company_client.post(
        reverse('collectionrequest-complete', args=[collection_request.pk]),
        {'actual_amount': '140'},
        format='json',
    )

    inst_client = APIClient()
    inst_client.force_authenticate(user=institution_user)
    confirm_url = reverse('collectionrequest-confirm-completion', args=[collection_request.pk])
    resp = inst_client.post(confirm_url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['status'] == 'completed'

    collection_request.refresh_from_db()
    assert collection_request.status == CollectionRequest.Status.COMPLETED
    assert collection_request.completed_at is not None
