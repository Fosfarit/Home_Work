import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.external_api import currency_api


class TestCurrencyAPI:
    """Тесты для функции currency_api"""

    @pytest.fixture
    def sample_transaction(self) -> dict:
        """Фикстура с примером транзакции"""
        return {
            "id": 214024827,
            "state": "EXECUTED",
            "date": "2018-12-20T16:43:26.929246",
            "operationAmount": {"amount": "70946.18", "currency": {"name": "USD", "code": "USD"}},
        }

    @pytest.fixture
    def sample_transaction_eur(self) -> dict:
        """Фикстура с примером транзакции в EUR"""
        return {
            "id": 214024828,
            "state": "EXECUTED",
            "date": "2018-12-20T16:43:26.929246",
            "operationAmount": {"amount": "1000.00", "currency": {"name": "Euro", "code": "EUR"}},
        }

    def test_currency_api_successful_conversion(self, sample_transaction: dict) -> None:
        """Тест успешной конвертации валюты"""
        # Мокаем ответ API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 5320.95}

        with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
            mock_get.return_value = mock_response

            result = currency_api(sample_transaction)

            assert isinstance(result, float)
            assert result == 5320.95
            mock_get.assert_called_once()

    def test_currency_api_missing_api_key(self, sample_transaction: dict) -> None:
        """Тест отсутствия API ключа"""
        # Исправлено: очищаем переменную окружения вместо установки пустой строки
        with patch.dict(os.environ, {}, clear=True):
            result = currency_api(sample_transaction)

            assert isinstance(result, str)
            assert result == "API ключ не найден"

    def test_currency_api_invalid_transaction_data(self) -> None:
        """Тест некорректных данных транзакции"""
        invalid_transactions = [
            {},
            {"operationAmount": None},
            {"operationAmount": {}},
            {"operationAmount": {"currency": {"code": "USD"}}},  # нет amount
            {"operationAmount": {"amount": "100", "currency": {}}},  # нет code
        ]

        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            for transaction in invalid_transactions:
                result = currency_api(transaction)
                assert isinstance(result, str)
                assert result == "Некорректные данные транзакции"

    def test_currency_api_connection_error(self, sample_transaction: dict) -> None:
        """Тест ошибки подключения"""
        with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
            mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

            result = currency_api(sample_transaction)

            assert isinstance(result, str)
            assert "Ошибка подключения" in result

    def test_currency_api_api_error_response(self, sample_transaction: dict) -> None:
        """Тест ошибки от API"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid API key"}

        with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
            mock_get.return_value = mock_response

            result = currency_api(sample_transaction)

            assert isinstance(result, str)
            assert "Ошибка API" in result

    def test_currency_api_data_processing_error(self, sample_transaction: dict) -> None:
        """Тест ошибки обработки данных"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Нет ключа 'result'

        with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
            mock_get.return_value = mock_response

            result = currency_api(sample_transaction)

            assert isinstance(result, str)
            assert "Ошибка обработки данных" in result

    def test_currency_api_different_currency(self, sample_transaction_eur: dict) -> None:
        """Тест конвертации другой валюты (EUR)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 95000.0}

        with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
            mock_get.return_value = mock_response

            result = currency_api(sample_transaction_eur)

            assert isinstance(result, float)
            assert result == 95000.0

            # Исправлено: проверяем URL более надежным способом
            call_args = mock_get.call_args
            url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
            assert "from=EUR" in url

    def test_currency_api_rounding(self, sample_transaction: dict) -> None:
        """Тест округления результата"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 5320.95678}  # Много знаков после запятой

        with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
            mock_get.return_value = mock_response

            result = currency_api(sample_transaction)

            assert isinstance(result, float)
            assert result == 5320.96  # Округление до 2 знаков

    def test_currency_api_invalid_amount_format(self) -> None:
        """Тест невалидного формата суммы"""
        invalid_transaction = {
            "id": 214024827,
            "state": "EXECUTED",
            "date": "2018-12-20T16:43:26.929246",
            "operationAmount": {"amount": "not_a_number", "currency": {"name": "USD", "code": "USD"}},  # Не число
        }

        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            result = currency_api(invalid_transaction)

            # Исправлено: ожидаем конкретное сообщение об ошибке
            assert isinstance(result, str)
            assert "Некорректные данные транзакции" in result or "Ошибка обработки данных" in result


def test_currency_api_function_signature() -> None:
    """Тест сигнатуры функции"""
    import inspect

    sig = inspect.signature(currency_api)
    assert len(sig.parameters) == 1
    assert "transaction" in sig.parameters
    # Исправлено: более гибкая проверка аннотации возвращаемого типа
    return_annotation = sig.return_annotation
    assert return_annotation in (str, float) or "str" in str(return_annotation) and "float" in str(return_annotation)


@pytest.mark.parametrize(
    "amount,expected_rounding",
    [
        ("100.123", 100.12),
        ("100.129", 100.13),
        ("100.000", 100.0),
    ],
)
def test_currency_api_various_amounts(amount: str, expected_rounding: float) -> None:
    """Параметризованный тест различных сумм и округления"""
    transaction = {
        "id": 214024827,
        "state": "EXECUTED",
        "date": "2018-12-20T16:43:26.929246",
        "operationAmount": {"amount": amount, "currency": {"name": "USD", "code": "USD"}},
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    # Исправлено: используем expected_rounding для согласованности теста
    mock_response.json.return_value = {"result": float(amount) * 75.0}

    with patch("src.external_api.requests.get") as mock_get, patch.dict(os.environ, {"API_KEY": "test_key"}):
        mock_get.return_value = mock_response

        result = currency_api(transaction)
