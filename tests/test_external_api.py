from unittest.mock import Mock, patch

import pytest

from src.external_api import currency_api


@pytest.fixture
def sample_transactions():
    """Фикстура с примером транзакций для тестирования"""
    return [
        {
            "id": 214024827,
            "state": "EXECUTED",
            "date": "2018-12-20T16:43:26.929246",
            "operationAmount": {"amount": "70946.18", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 10848359769870775355",
            "to": "Счет 21969751544412966366",
        },
        {
            "id": 522357576,
            "state": "EXECUTED",
            "date": "2019-07-12T20:41:47.882230",
            "operationAmount": {"amount": "51463.70", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 48894435694657014368",
            "to": "Счет 38976430693692818358",
        },
    ]


@pytest.fixture
def mock_api_response():
    """Фикстура с мок-ответом от API"""
    return {
        "success": True,
        "query": {"from": "USD", "to": "RUB", "amount": 100},
        "info": {"timestamp": 1699999999, "rate": 95.5},
        "date": "2023-11-15",
        "result": 9550.0,
    }


class TestCurrencyAPI:
    """Тесты для функции currency_api"""

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_currency_api_success(self, mock_getenv, mock_requests_get, sample_transactions, mock_api_response):
        """Тест успешного выполнения функции с корректными данными"""
        # Мокаем получение API ключа
        mock_getenv.return_value = "test_api_key"

        # Мокаем ответ от API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_requests_get.return_value = mock_response

        # Вызываем тестируемую функцию
        result = currency_api(sample_transactions)

        # Проверяем, что функция вернула корректный результат
        expected_amount = (70946.18 * 95.5) + (51463.70 * 95.5)
        expected_result = round(expected_amount, 2)
        assert result == expected_result

        # Проверяем, что requests.get вызывался правильное количество раз
        assert mock_requests_get.call_count == len(sample_transactions)

        # Проверяем, что headers передавались корректно
        for call in mock_requests_get.call_args_list:
            args, kwargs = call
            assert kwargs["headers"] == {"apikey": "test_api_key"}

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_currency_api_different_currencies(self, mock_getenv, mock_requests_get, mock_api_response):
        """Тест с разными валютами"""
        # Подготавливаем тестовые данные с разными валютами
        transactions = [
            {"id": 1, "operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}},
            {"id": 2, "operationAmount": {"amount": "200.00", "currency": {"code": "EUR"}}},
        ]

        # Настраиваем моки
        mock_getenv.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_requests_get.return_value = mock_response

        # Вызываем функцию
        result = currency_api(transactions)

        # Проверяем результат
        expected_amount = (100.00 * 95.5) + (200.00 * 95.5)
        expected_result = round(expected_amount, 2)
        assert result == expected_result

        # Проверяем, что URL формировался правильно для разных валют
        calls = mock_requests_get.call_args_list
        assert "from=USD" in calls[0][0][0]  # Первый вызов для USD
        assert "from=EUR" in calls[1][0][0]  # Второй вызов для EUR

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_currency_api_failure(self, mock_getenv, mock_requests_get, sample_transactions):
        """Тест обработки ошибки API"""
        # Настраиваем моки для ошибки
        mock_getenv.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response

        # Вызываем функцию
        result = currency_api(sample_transactions)

        # Проверяем, что возвращается сообщение об ошибке
        assert result == "Ошибка подключения к API"

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_currency_api_network_error(self, mock_getenv, mock_requests_get, sample_transactions):
        """Тест обработки сетевой ошибки"""
        # Настраиваем моки для выброса исключения
        mock_getenv.return_value = "test_api_key"
        mock_requests_get.side_effect = Exception("Network error")

        # Вызываем функцию
        result = currency_api(sample_transactions)

        # Проверяем, что возвращается сообщение об ошибке
        assert result == "Ошибка подключения к API"

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_currency_api_empty_transactions(self, mock_getenv, mock_requests_get):
        """Тест с пустым списком транзакций"""
        # Настраиваем моки
        mock_getenv.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 100.0}
        mock_requests_get.return_value = mock_response

        # Вызываем функцию с пустым списком
        result = currency_api([])

        # Проверяем, что возвращается 0 для пустого списка
        assert result == 0.0
        # Проверяем, что API не вызывалось
        mock_requests_get.assert_not_called()

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_currency_api_rounding(self, mock_getenv, mock_requests_get, mock_api_response):
        """Тест корректного округления результата"""
        # Настраиваем моки
        mock_getenv.return_value = "test_api_key"
        mock_response = Mock()
        mock_response.status_code = 200

        # Меняем курс для проверки округления
        mock_api_response_modified = mock_api_response.copy()
        mock_api_response_modified["result"] = 123.456789
        mock_response.json.return_value = mock_api_response_modified
        mock_requests_get.return_value = mock_response

        transactions = [{"id": 1, "operationAmount": {"amount": "1.00", "currency": {"code": "USD"}}}]

        # Вызываем функцию
        result = currency_api(transactions)

        # Проверяем корректное округление до 2 знаков
        assert result == 123.46

    @patch("src.external_api.requests.get")
    @patch("src.external_api.os.getenv")
    def test_api_key_usage(self, mock_getenv, mock_requests_get, sample_transactions, mock_api_response):
        """Тест корректного использования API ключа"""
        # Настраиваем моки
        test_api_key = "test_secret_key_123"
        mock_getenv.return_value = test_api_key

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_requests_get.return_value = mock_response

        # Вызываем функцию
        currency_api(sample_transactions)

        # Проверяем, что API ключ передавался в headers
        mock_requests_get.assert_called()
        for call in mock_requests_get.call_args_list:
            args, kwargs = call
            assert kwargs["headers"] == {"apikey": test_api_key}
