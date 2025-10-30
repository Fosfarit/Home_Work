import os
from typing import List, Dict, Any

from src.utils import read_json_file
from src.read_files_csv_and_xlsx import read_CSV_file, read_xlsx_file
from src.processing import filter_by_state, sort_by_date
from src.widget import mask_account_card, get_date
from src.generators import filter_by_currency, transaction_descriptions
from src.filter_bank_transactions_by_word import process_bank_search
from src.external_api import currency_api
from src.decorators import log


@log("main.log")
def get_transactions_from_file(file_type: str) -> List[Dict[str, Any]]:
    """Получение транзакций из файла в зависимости от типа"""
    if file_type == "1":
        file_path = "data/operations.json"
        return read_json_file(file_path)
    elif file_type == "2":
        file_path = "data/transactions.csv"
        return read_CSV_file(file_path)
    elif file_type == "3":
        file_path = "data/transactions_excel.xlsx"
        return read_xlsx_file(file_path)
    else:
        raise ValueError("Неверный тип файла")


@log("main.log")
def get_valid_status() -> str:
    """Получение валидного статуса от пользователя"""
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    while True:
        status = input("Введите статус, по которому необходимо выполнить фильтрацию. \n"
                       "Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING\n").upper()

        if status in valid_statuses:
            print(f"Операции отфильтрованы по статусу '{status}'")
            return status
        else:
            print(f"Статус операции '{status}' недоступен.")


@log("main.log")
def get_user_preferences() -> Dict[str, Any]:
    """Получение предпочтений пользователя для фильтрации"""
    preferences = {}

    # Сортировка по дате
    sort_date = input("Отсортировать операции по дате? Да/Нет\n").lower()
    if sort_date == "да":
        sort_order = input("Отсортировать по возрастанию или по убыванию?\n").lower()
        preferences["sort_date"] = True
        preferences["sort_ascending"] = "возрастанию" in sort_order
    else:
        preferences["sort_date"] = False

    # Фильтрация по рублевым транзакциям
    rub_only = input("Выводить только рублевые транзакции? Да/Нет\n").lower()
    preferences["rub_only"] = rub_only == "да"

    # Фильтрация по слову в описании
    filter_word = input("Отфильтровать список транзакций по определенному слову в описании? Да/Нет\n").lower()
    if filter_word == "да":
        preferences["search_word"] = input("Введите слово для поиска в описании: ")
    else:
        preferences["search_word"] = None

    return preferences


@log("main.log")
def format_transaction_amount(transaction: Dict[str, Any]) -> str:
    """Форматирование суммы транзакции"""
    operation_amount = transaction.get("operationAmount", {})
    amount = operation_amount.get("amount", "0")
    currency = operation_amount.get("currency", {})
    currency_code = currency.get("code", "")

    if currency_code == "RUB":
        return f"{amount} руб."
    else:
        # Пытаемся конвертировать через API
        converted = currency_api(transaction)
        if isinstance(converted, (int, float)):
            return f"{amount} {currency_code} (~{converted} руб.)"
        else:
            return f"{amount} {currency_code}"


@log("main.log")
def format_transaction(transaction: Dict[str, Any]) -> str:
    """Форматирование транзакции для вывода"""
    date = get_date(transaction.get("date", ""))
    description = transaction.get("description", "")
    amount = format_transaction_amount(transaction)

    # Форматирование отправителя и получателя
    from_account = transaction.get("from")
    to_account = transaction.get("to")

    formatted_from = mask_account_card(from_account) if from_account else ""
    formatted_to = mask_account_card(to_account) if to_account else ""

    result = f"{date} {description}\n"

    if formatted_from and formatted_to:
        result += f"{formatted_from} -> {formatted_to}\n"
    elif formatted_to:
        result += f"{formatted_to}\n"

    result += f"Сумма: {amount}\n"

    return result


@log("main.log")
def main() -> None:
    """Основная функция программы"""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    file_type = input()

    try:
        # Получение транзакций из файла
        if file_type == "1":
            print("Для обработки выбран JSON-файл.")
        elif file_type == "2":
            print("Для обработки выбран CSV-файл.")
        elif file_type == "3":
            print("Для обработки выбран XLSX-файл.")
        else:
            print("Неверный выбор. Завершение программы.")
            return

        transactions = get_transactions_from_file(file_type)

        # Фильтрация по статусу
        status = get_valid_status()
        filtered_transactions = filter_by_state(transactions, status)

        # Получение предпочтений пользователя
        preferences = get_user_preferences()

        # Применение фильтров
        processed_transactions = filtered_transactions.copy()

        # Сортировка по дате
        if preferences["sort_date"]:
            processed_transactions = sort_by_date(processed_transactions, preferences["sort_ascending"])

        # Фильтрация по рублевым транзакциям
        if preferences["rub_only"]:
            processed_transactions = list(filter_by_currency(processed_transactions, "RUB"))

        # Фильтрация по слову в описании
        if preferences["search_word"]:
            processed_transactions = process_bank_search(processed_transactions, preferences["search_word"])

        # Вывод результатов
        print("Распечатываю итоговый список транзакций...")
        print(f"\nВсего банковских операций в выборке: {len(processed_transactions)}\n")

        if not processed_transactions:
            print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
            return

        for transaction in processed_transactions:
            print(format_transaction(transaction))
            print()

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()