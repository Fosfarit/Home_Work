import os
import requests
from dotenv import load_dotenv

load_dotenv()


def currency_api(transaction: dict) -> str | float:
    """Функция конвертации валюты"""

    token_api = os.getenv("API_KEY")

    # Проверяем наличие API ключа
    if not token_api:
        return "API ключ не найден"

    headers = {"apikey": token_api}
    base_url = "https://api.apilayer.com/exchangerates_data/convert"

    # Получаем данные о транзакции
    operation_amount = transaction.get("operationAmount")
    if not operation_amount:
        return "Некорректные данные транзакции"

    currency_code = operation_amount["currency"]["code"]
    amount = float(operation_amount["amount"])

    # Формируем URL для API запроса
    url = f"{base_url}?to=RUB&from={currency_code}&amount={amount}"

    try:
        response = requests.get(url, headers=headers)
        result_response = response.json()

        if response.status_code == 200:
            return round(float(result_response["result"]), 2)
        else:
            return f"Ошибка API: {result_response.get('error', 'Неизвестная ошибка')}"

    except requests.exceptions.RequestException as e:
        return f"Ошибка подключения: {e}"
    except (KeyError, ValueError) as e:
        return f"Ошибка обработки данных: {e}"


# transaction = {
#     "id": 214024827,
#     "state": "EXECUTED",
#     "date": "2018-12-20T16:43:26.929246",
#     "operationAmount": {
#         "amount": "70946.18",
#         "currency": {
#             "name": "USD",
#             "code": "USD"
#         }
#     }
# }
#
# print(currency_api(transaction))