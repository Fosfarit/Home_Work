from typing import Any, Dict, Hashable, List

from src.decorators import log
from src.external_api import currency_api
from src.filter_bank_transactions_by_word import process_bank_search
from src.generators import filter_by_currency
from src.processing import filter_by_state, sort_by_date
from src.read_files_csv_and_xlsx import read_CSV_file, read_xlsx_file
from src.utils import read_json_file
from src.widget import get_date, mask_account_card


@log("main.log")
def get_transactions_from_file(file_type: str) -> List[Dict[str, Any]]:
    """Получение транзакций из файла в зависимости от типа"""
    try:
        if file_type == "1":
            file_path = "data/operations.json"
            transactions = read_json_file(file_path)
        elif file_type == "2":
            file_path = "data/transactions.csv"
            transactions = read_CSV_file(file_path)
        elif file_type == "3":
            file_path = "data/transactions_excel.xlsx"
            transactions = read_xlsx_file(file_path)
        else:
            raise ValueError("Неверный тип файла")

        # Приводим типы ключей к str для совместимости
        return [_convert_keys_to_str(transaction) for transaction in transactions]

    except FileNotFoundError:
        print(f"Файл не найден по пути: {file_path}")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


def _convert_keys_to_str(transaction: Dict[Hashable, Any]) -> Dict[str, Any]:
    """Конвертирует ключи словаря в строковый тип"""
    return {str(key): value for key, value in transaction.items()}


@log("main.log")
def get_valid_status() -> str:
    """Получение валидного статуса от пользователя"""
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    while True:
        status = input(
            "Введите статус, по которому необходимо выполнить фильтрацию. \n"
            "Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING\n"
        ).upper()

        if status in valid_statuses:
            print(f"Операции отфильтрованы по статусу '{status}'")
            return status
        else:
            print(f"Статус операции '{status}' недоступен.")


@log("main.log")
def get_user_preferences() -> Dict[str, Any]:
    """Получение предпочтений пользователя для фильтрации"""
    preferences: Dict[str, Any] = {}

    # Сортировка по дате
    while True:
        sort_date = input("Отсортировать операции по дате? Да/Нет\n").lower()
        if sort_date in ["да", "нет"]:
            preferences["sort_date"] = sort_date == "да"
            break
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'")

    if preferences["sort_date"]:
        while True:
            sort_order = input("Отсортировать по возрастанию или по убыванию?\n").lower()
            if "возрастанию" in sort_order or "убыванию" in sort_order:
                preferences["sort_ascending"] = "возрастанию" in sort_order
                break
            else:
                print("Пожалуйста, введите 'по возрастанию' или 'по убыванию'")

    # Фильтрация по рублевым транзакциям
    while True:
        rub_only = input("Выводить только рублевые транзакции? Да/Нет\n").lower()
        if rub_only in ["да", "нет"]:
            preferences["rub_only"] = rub_only == "да"
            break
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'")

    # Фильтрация по слову в описании
    while True:
        filter_word = input("Отфильтровать список транзакций по определенному слову в описании? Да/Нет\n").lower()
        if filter_word in ["да", "нет"]:
            if filter_word == "да":
                search_word_input = input("Введите слово для поиска в описании: ").strip()
                preferences["search_word"] = search_word_input if search_word_input else None
            else:
                preferences["search_word"] = None
            break
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'")

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
        try:
            converted = currency_api(transaction)
            if isinstance(converted, (int, float)):
                return f"{amount} {currency_code} (~{converted:.2f} руб.)"
            else:
                return f"{amount} {currency_code}"
        except Exception:
            return f"{amount} {currency_code}"


@log("main.log")
def format_transaction(transaction: Dict[str, Any]) -> str:
    """Форматирование транзакции для вывода"""
    date = get_date(transaction.get("date", "")) or "Дата не указана"
    description = transaction.get("description", "Описание отсутствует")
    amount = format_transaction_amount(transaction)

    # Форматирование отправителя и получателя
    from_account = transaction.get("from")
    to_account = transaction.get("to")

    formatted_from = mask_account_card(from_account) if from_account else ""
    formatted_to = mask_account_card(to_account) if to_account else ""

    result = f"{date} {description}\n"

    if formatted_from and formatted_to:
        result += f"{formatted_from} -> {formatted_to}\n"
    elif formatted_from:
        result += f"{formatted_from}\n"
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

    file_type = input().strip()

    # Проверка валидности выбора файла
    if file_type not in ["1", "2", "3"]:
        print("Неверный выбор. Завершение программы.")
        return

    try:
        # Получение транзакций из файла
        if file_type == "1":
            print("Для обработки выбран JSON-файл.")
        elif file_type == "2":
            print("Для обработки выбран CSV-файл.")
        elif file_type == "3":
            print("Для обработки выбран XLSX-файл.")

        transactions = get_transactions_from_file(file_type)

        # Проверка, что транзакции были успешно загружены
        if not transactions:
            print("Не удалось загрузить транзакции из файла. Завершение программы.")
            return

        # Фильтрация по статусу
        status = get_valid_status()
        filtered_transactions = filter_by_state(transactions, status)

        # Проверка, что после фильтрации по статусу есть транзакции
        if not filtered_transactions:
            print("Не найдено транзакций с указанным статусом.")
            return

        # Получение предпочтений пользователя
        preferences = get_user_preferences()

        # Применение фильтров
        processed_transactions = filtered_transactions.copy()

        # Сортировка по дате
        if preferences["sort_date"]:
            processed_transactions = sort_by_date(processed_transactions, preferences["sort_ascending"])

        # Фильтрация по рублевым транзакциям
        if preferences["rub_only"]:
            # Преобразуем генератор в список
            processed_transactions = list(filter_by_currency(processed_transactions, "RUB"))

        # Фильтрация по слову в описании
        search_word = preferences.get("search_word")
        if search_word:
            processed_transactions = process_bank_search(processed_transactions, search_word)

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
