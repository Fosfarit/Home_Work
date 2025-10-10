from typing import Generator


def filter_by_currency(transactions: list[dict], name_currency: str = "EUR") -> Generator:
    """Функцию, которая принимает на вход список словарей,
    представляющих транзакции и возвращает итератор,
    который поочередно выдает транзакции,
    где валюта операции соответствует заданной (например, USD).
    """
    for transaction in transactions:
        if transaction.get("operationAmount", {}).get("currency").get("code") == name_currency:
            yield transaction


def transaction_descriptions(transactions: list[dict]) -> Generator:
    """
    Генератор, который принимает список словарей с транзакциями и
    возвращает описание каждой операции по очереди.
    """
    yield from (transaction.get("description", []) for transaction in transactions)


def card_number_generator(start: int, stop: int) -> Generator:
    """
    Генератор, который выдает номера банковских карт в формате XXXX XXXX XXXX XXXX,
    где X — цифра номера карты. Генератор может сгенерировать номера карт в заданном диапазоне
    от 0000 0000 0000 0001 до 9999 9999 9999 9999.
    Генератор должен принимать начальное и конечное значения для генерации диапазона номеров.
    """
    for number in range(start, stop + 1):
        if number <= 999999999999:
            number_card = str(number).zfill(16)
            yield f"{number_card[:3]} {number_card[4:8]} {number_card[8:12]} {number_card[12:16]}"
