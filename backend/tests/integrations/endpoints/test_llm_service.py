import pytest
from unittest.mock import patch, MagicMock
from integrations.llm_service import get_ai_advice


@patch('integrations.llm_service.genai.GenerativeModel')
def test_get_ai_advice_success(mock_model_class):
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance

    mock_response = MagicMock()
    mock_response.text = "Mocked advice: Save more money!"
    mock_model_instance.generate_content.return_value = mock_response

    comparison_data = {
        'Groceries': {'current': 100, 'previous': 80, 'diff_percent': 25.0}
    }
    transactions = [
        {'date': '2023-11-25', 'amount': 50, 'category_name': 'Groceries', 'description': 'Milk'}
    ]

    # Виклик функції
    result = get_ai_advice(comparison_data, transactions)

    assert result == "Mocked advice: Save more money!"
    mock_model_instance.generate_content.assert_called_once()

    call_args = mock_model_instance.generate_content.call_args[0][0]
    assert "Groceries" in call_args
    assert "25.0%" in call_args


@patch('integrations.llm_service.genai.GenerativeModel')
def test_get_ai_advice_api_error(mock_model_class):
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance
    mock_model_instance.generate_content.side_effect = Exception("API Error")

    result = get_ai_advice({}, [])

    assert result is None