import pytest
from splitting.models import SharedSpent, SharedSpentMember

pytestmark = pytest.mark.django_db
URL = '/api/splitting/spents/'


@pytest.fixture
def shared_spent_payload(standard_category, user2):
    return {
        "category": standard_category.id,
        "total_amount": 1000.00,
        "date": "2025-11-15",
        "participants": [
            {"user_id": user2.id, "amount": 300.00}
        ]
    }


def test_create_shared_spent_success(
        authenticated_client, shared_spent_payload, user, user2
):
    response = authenticated_client.post(URL, shared_spent_payload, format='json')

    assert response.status_code == 201
    assert SharedSpent.objects.count() == 1
    assert SharedSpentMember.objects.count() == 2

    owner_part = SharedSpentMember.objects.get(user=user)
    assert owner_part.amount == 700.00
    assert owner_part.is_owner_part is True


def test_create_shared_spent_fail_sum_too_high(
        authenticated_client, shared_spent_payload
):
    shared_spent_payload['participants'][0]['amount'] = 1100.00
    response = authenticated_client.post(URL, shared_spent_payload, format='json')

    assert response.status_code == 400
    assert 'participants' in response.data


def test_participant_leave_spent_success(
        authenticated_client, shared_spent_payload, user, user2, api_client
):
    create_response = authenticated_client.post(URL, shared_spent_payload, format='json')
    spent_id = create_response.data['id']

    client_user2 = api_client
    client_user2.force_authenticate(user=user2)

    leave_url = f"{URL}{spent_id}/leave/"
    leave_response = client_user2.post(leave_url)

    assert leave_response.status_code == 200

    assert SharedSpentMember.objects.count() == 1

    owner_part = SharedSpentMember.objects.get(user=user)
    assert owner_part.amount == 1000.00


def test_owner_delete_spent_success(authenticated_client, shared_spent_payload):
    response = authenticated_client.post(URL, shared_spent_payload, format='json')
    spent_id = response.data['id']

    delete_response = authenticated_client.delete(f"{URL}{spent_id}/")

    assert delete_response.status_code == 204
    assert SharedSpent.objects.count() == 0
    assert SharedSpentMember.objects.count() == 0


def test_participant_delete_spent_fails(
        authenticated_client, shared_spent_payload, user2, api_client
):
    response = authenticated_client.post(URL, shared_spent_payload, format='json')
    spent_id = response.data['id']

    client_user2 = api_client
    client_user2.force_authenticate(user=user2)
    delete_response = client_user2.delete(f"{URL}{spent_id}/")

    assert delete_response.status_code == 403
    assert SharedSpent.objects.count() == 1
