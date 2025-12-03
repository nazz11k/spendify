import pytest
from unittest.mock import patch
from integrations.models import FinancialAdvice
from transactions.models import Transaction, Category

pytestmark = pytest.mark.django_db
URL = '/api/integrations/advice/'


def test_get_advice_history_empty(authenticated_client):
    response = authenticated_client.get(URL)
    assert response.status_code == 200
    assert response.data == []


def test_get_advice_history_with_data(authenticated_client, user):
    FinancialAdvice.objects.create(user=user, advices="Old advice")

    response = authenticated_client.get(URL)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['advices'] == "Old advice"


@patch('integrations.views.get_ai_advice')
def test_generate_new_advice_success(mock_get_advice, authenticated_client, user):
    cat = Category.objects.create(name="Food", type="EXPENSE", owner=user)
    Transaction.objects.create(owner=user, category=cat, amount=100, date="2025-11-01")

    mock_get_advice.return_value = "New AI Advice generated."

    response = authenticated_client.post(URL)

    assert response.status_code == 201
    assert response.data['advices'] == "New AI Advice generated."

    assert FinancialAdvice.objects.count() == 1
    assert FinancialAdvice.objects.first().advices == "New AI Advice generated."


@patch('integrations.views.get_ai_advice')
def test_generate_advice_service_unavailable(mock_get_advice, authenticated_client, user):
    cat = Category.objects.create(name="Food", type="EXPENSE", owner=user)
    Transaction.objects.create(owner=user, category=cat, amount=100, date="2025-11-01")

    mock_get_advice.return_value = None

    response = authenticated_client.post(URL)

    assert response.status_code == 503
    assert FinancialAdvice.objects.count() == 0