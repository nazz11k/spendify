import pytest
from datetime import date
from transactions.models import Transaction, Category
from splitting.models import SharedSpent, SharedSpentMember

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data(user, user2):
    cat_food = Category.objects.create(name="Food", type="EXPENSE", owner=None)
    cat_transport = Category.objects.create(name="Transport", type="EXPENSE", owner=None)

    Transaction.objects.create(
        owner=user,
        category=cat_food,
        amount=100.00,
        date=date.today()
    )

    shared = SharedSpent.objects.create(
        owner=user2,
        category=cat_transport,
        total_amount=500.00,
        date=date.today()
    )
    SharedSpentMember.objects.create(
        shared_spent=shared,
        user=user,
        amount=200.00,
        is_owner_part=False
    )


def test_activity_report(authenticated_client, setup_data):
    url = '/api/reports/activity/'
    response = authenticated_client.get(url)

    assert response.status_code == 200
    data = response.data

    assert len(data) == 2

    types = {item['type'] for item in data}
    assert 'personal' in types
    assert 'shared' in types

    amounts = {float(item['amount']) for item in data}
    assert 100.0 in amounts
    assert 200.0 in amounts


def test_category_summary_report(authenticated_client, setup_data):
    url = '/api/reports/by-category/'
    response = authenticated_client.get(url)

    assert response.status_code == 200

    assert float(response.data['total_spent']) == 300.00

    breakdown = response.data['breakdown']
    assert len(breakdown) == 2

    transport_data = next(item for item in breakdown if item['category'] == 'Transport')
    assert float(transport_data['total_amount']) == 200.00

    assert 66.0 < transport_data['percentage'] < 67.0


def test_over_time_report(authenticated_client, setup_data):
    url = '/api/reports/over-time/'
    response = authenticated_client.get(url)

    assert response.status_code == 200

    today_str = date.today().isoformat()
    today_entry = next((item for item in response.data if item['date'] == today_str), None)

    assert today_entry is not None
    assert float(today_entry['total_amount']) == 300.00