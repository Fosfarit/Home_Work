import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.external_api import currency_api


@pytest.fixture
def mock_transaction():
    """Фикстура с тестовой транзакцией"""
    return {
        "id": 214024827,
        "state": "EXECUTED",
        "date": "2018-12-20T16:43:26.929246",
        "operationAmount": {
            "amount": "70946.18",
            "currency": {"name": "USD", "code": "USD"}
        },
    }


@pytest.fixture
def mock_transaction_without_amount():
    """Фикстура с транзакцией без operationAmount"""
    return {
        "id": 214024827,
        "state": "EXECUTED",
        "date": "2018-12-20T16:43:26.929246"
    }


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_success(mock_requests_get, mock_transaction):
    """Тест успешного выполнения конвертации валюты"""
    # Мокаем ответ API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": 5320.95}
    mock_requests_get.return_value = mock_response

    result = currency_api(mock_transaction)

    # Проверяем вызов API с правильными параметрами
    expected_url = "https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=USD&amount=70946.18"
    mock_requests_get.assert_called_once_with(
        expected_url,
        headers={"apikey": "test_api_key"}
    )

    # Проверяем результат
    assert result == 5320.95


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_api_error(mock_requests_get, mock_transaction):
    """Тест обработки ошибки от API"""
    # Мокаем ответ с ошибкой
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Invalid currency code"}
    mock_requests_get.return_value = mock_response

    result = currency_api(mock_transaction)

    assert result == "Ошибка API: Invalid currency code"


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_connection_error(mock_requests_get, mock_transaction):
    """Тест обработки ошибки подключения"""
    # Мокаем исключение при запросе
    mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    result = currency_api(mock_transaction)

    assert result == "Ошибка подключения: Connection failed"


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_key_error(mock_requests_get, mock_transaction):
    """Тест обработки ошибки ключа в ответе"""
    # Мокаем ответ без ключа 'result'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "some data"}  # Нет ключа 'result'
    mock_requests_get.return_value = mock_response

    result = currency_api(mock_transaction)

    assert "Ошибка обработки данных" in result


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_value_error(mock_requests_get, mock_transaction):
    """Тест обработки ошибки преобразования данных"""
    # Мокаем ответ с некорректными данными для float
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "not_a_number"}
    mock_requests_get.return_value = mock_response

    result = currency_api(mock_transaction)

    assert "Ошибка обработки данных" in result


def test_currency_api_no_api_key(mock_transaction):
    """Тест отсутствия API ключа"""
    # Убеждаемся, что API_KEY не установлен
    with patch.dict(os.environ, {}, clear=True):
        result = currency_api(mock_transaction)
        assert result == "API ключ не найден"


def test_currency_api_no_operation_amount(mock_transaction_without_amount):
    """Тест отсутствия operationAmount в транзакции"""
    with patch.dict(os.environ, {"API_KEY": "test_api_key"}):
        result = currency_api(mock_transaction_without_amount)

    assert result == "Некорректные данные транзакции"


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_different_currency(mock_requests_get):
    """Тест конвертации другой валюты"""
    # Транзакция с EUR
    eur_transaction = {
        "id": 214024828,
        "state": "EXECUTED",
        "date": "2018-12-21T16:43:26.929246",
        "operationAmount": {
            "amount": "1000.00",
            "currency": {"name": "Euro", "code": "EUR"}
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": 85000.0}
    mock_requests_get.return_value = mock_response

    result = currency_api(eur_transaction)

    # Исправлено: учитываем, что "1000.00" преобразуется в 1000.0
    expected_url = "https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=EUR&amount=1000.0"
    mock_requests_get.assert_called_once_with(
        expected_url,
        headers={"apikey": "test_api_key"}
    )

    assert result == 85000.0


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_rounding(mock_requests_get, mock_transaction):
    """Тест округления результата"""
    # Мокаем ответ с длинным числом
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": 5320.957823}
    mock_requests_get.return_value = mock_response

    result = currency_api(mock_transaction)

    # Проверяем округление до 2 знаков
    assert result == 5320.96


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_zero_amount(mock_requests_get):
    """Тест обработки нулевой суммы"""
    transaction_zero_amount = {
        "id": 214024832,
        "state": "EXECUTED",
        "date": "2018-12-25T16:43:26.929246",
        "operationAmount": {
            "amount": "0",
            "currency": {"name": "CHF", "code": "CHF"}
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": 0.0}
    mock_requests_get.return_value = mock_response

    result = currency_api(transaction_zero_amount)

    expected_url = "https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=CHF&amount=0.0"
    mock_requests_get.assert_called_once_with(
        expected_url,
        headers={"apikey": "test_api_key"}
    )

    assert result == 0.0


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch('src.external_api.requests.get')
def test_currency_api_negative_amount(mock_requests_get):
    """Тест обработки отрицательной суммы"""
    transaction_negative_amount = {
        "id": 214024833,
        "state": "EXECUTED",
        "date": "2018-12-26T16:43:26.929246",
        "operationAmount": {
            "amount": "-100.50",
            "currency": {"name": "AUD", "code": "AUD"}
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": -7500.0}
    mock_requests_get.return_value = mock_response

    result = currency_api(transaction_negative_amount)

    expected_url = "https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=AUD&amount=-100.5"
    mock_requests_get.assert_called_once_with(
        expected_url,
        headers={"apikey": "test_api_key"}
    )

    assert result == -7500.0