import os

import requests
from dotenv import load_dotenv

load_dotenv()


def currency_api(transactions: list[dict]) -> float:
    """Функция конвертации валюты"""

    token_api = os.getenv("API_KEY")

    amount = []

    for transaction in transactions:
        headers = {"apikey": token_api}
        base_url = "https://api.apilayer.com/exchangerates_data/convert"
        url = f"{base_url}?to={"RUB"}&from={
        transaction["operationAmount"]["currency"]["code"]}&amount={
        transaction["operationAmount"]["amount"]}"
        response = requests.get(url, headers=headers)
        result_response = response.json()
        if response.status_code == 200:
            amount.append(float(result_response["result"]))
        else:
            return "Ошибка подключения к API"

    return round(sum(amount), 2)
