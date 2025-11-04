from typing import Any, Dict, Hashable, List, Optional

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
        file_path = ""
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

        # Проверяем, что получили список
        if not isinstance(transactions, list):
            print(f"Ошибка: ожидался список транзакций, получен {type(transactions)}")
            return []

        # Приводим типы ключей к str для совместимости и проверяем структуру
        valid_transactions = []
        for transaction in transactions:
            if isinstance(transaction, dict):
                converted_transaction = _convert_keys_to_str(transaction)
                valid_transactions.append(converted_transaction)
            else:
                print(f"Пропущен некорректный элемент транзакции: {type(transaction)}")

        print(f"Успешно загружено {len(valid_transactions)} транзакций из {file_path}")
        return valid_transactions

    except FileNotFoundError:
        print(f"Файл не найден по пути: {file_path}")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


def _convert_keys_to_str(transaction: Dict[Hashable, Any]) -> Dict[str, Any]:
    """Конвертирует ключи словаря в строковый тип"""
    try:
        return {str(key): value for key, value in transaction.items()}
    except Exception as e:
        print(f"Ошибка при конвертации ключей: {e}")
        return {}


@log("main.log")
def get_valid_status() -> Optional[str]:
    """Получение валидного статуса от пользователя"""
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            status = (
                input(
                    "Введите статус, по которому необходимо выполнить фильтрацию. \n"
                    "Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING\n"
                )
                .strip()
                .upper()
            )

            if not status:
                print("Статус не может быть пустым. Попробуйте снова.")
                attempts += 1
                continue

            if status in valid_statuses:
                print(f"Операции отфильтрованы по статусу '{status}'")
                return status
            else:
                print(f"Статус операции '{status}' недоступен.")
                attempts += 1
                print(f"Осталось попыток: {max_attempts - attempts}")

        except (KeyboardInterrupt, EOFError):
            print("\nОперация прервана пользователем.")
            return None
        except Exception as e:
            print(f"Произошла ошибка при вводе: {e}")
            attempts += 1

    print("Превышено максимальное количество попыток. Используется статус по умолчанию: EXECUTED")
    return "EXECUTED"


@log("main.log")
def get_user_preferences() -> Dict[str, Any]:
    """Получение предпочтений пользователя для фильтрации"""
    preferences: Dict[str, Any] = {"sort_date": False, "sort_ascending": True, "rub_only": False, "search_word": None}

    try:
        # Сортировка по дате
        while True:
            try:
                sort_date = input("Отсортировать операции по дате? Да/Нет\n").strip().lower()
                if sort_date in ["да", "д", "yes", "y"]:
                    preferences["sort_date"] = True
                    break
                elif sort_date in ["нет", "н", "no", "n"]:
                    preferences["sort_date"] = False
                    break
                else:
                    print("Пожалуйста, введите 'Да' или 'Нет'")
            except (KeyboardInterrupt, EOFError):
                print("\nИспользуется значение по умолчанию: без сортировки")
                break
            except Exception as e:
                print(f"Ошибка ввода: {e}")

        if preferences["sort_date"]:
            while True:
                try:
                    sort_order = input("Отсортировать по возрастанию или по убыванию?\n").strip().lower()
                    if any(word in sort_order for word in ["возрастанию", "возрастание", "asc"]):
                        preferences["sort_ascending"] = True
                        break
                    elif any(word in sort_order for word in ["убыванию", "убывание", "desc"]):
                        preferences["sort_ascending"] = False
                        break
                    else:
                        print("Пожалуйста, введите 'по возрастанию' или 'по убыванию'")
                except (KeyboardInterrupt, EOFError):
                    print("\nИспользуется значение по умолчанию: по возрастанию")
                    break
                except Exception as e:
                    print(f"Ошибка ввода: {e}")

        # Фильтрация по рублевым транзакциям
        while True:
            try:
                rub_only = input("Выводить только рублевые транзакции? Да/Нет\n").strip().lower()
                if rub_only in ["да", "д", "yes", "y"]:
                    preferences["rub_only"] = True
                    break
                elif rub_only in ["нет", "н", "no", "n"]:
                    preferences["rub_only"] = False
                    break
                else:
                    print("Пожалуйста, введите 'Да' или 'Нет'")
            except (KeyboardInterrupt, EOFError):
                print("\nИспользуется значение по умолчанию: все валюты")
                break
            except Exception as e:
                print(f"Ошибка ввода: {e}")

        # Фильтрация по слову в описании
        while True:
            try:
                filter_word = (
                    input("Отфильтровать список транзакций по определенному слову в описании? Да/Нет\n")
                    .strip()
                    .lower()
                )
                if filter_word in ["да", "д", "yes", "y"]:
                    search_word_input = input("Введите слово для поиска в описании: ").strip()
                    if search_word_input:
                        preferences["search_word"] = search_word_input
                    else:
                        print("Пустая строка поиска. Фильтрация по слову отключена.")
                    break
                elif filter_word in ["нет", "н", "no", "n"]:
                    preferences["search_word"] = None
                    break
                else:
                    print("Пожалуйста, введите 'Да' или 'Нет'")
            except (KeyboardInterrupt, EOFError):
                print("\nИспользуется значение по умолчанию: без фильтрации по словам")
                break
            except Exception as e:
                print(f"Ошибка ввода: {e}")

    except Exception as e:
        print(f"Неожиданная ошибка при получении предпочтений: {e}")

    return preferences


@log("main.log")
def format_transaction_amount(transaction: Dict[str, Any]) -> str:
    """Форматирование суммы транзакции"""
    try:
        operation_amount = transaction.get("operationAmount", {})
        if not isinstance(operation_amount, dict):
            return "Сумма не указана"

        amount = operation_amount.get("amount", "0")
        currency = operation_amount.get("currency", {})

        if not isinstance(currency, dict):
            return f"{amount}"

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
    except Exception as e:
        print(f"Ошибка при форматировании суммы: {e}")
        return "Ошибка формата суммы"


@log("main.log")
def format_transaction(transaction: Dict[str, Any]) -> str:
    """Форматирование транзакции для вывода"""
    try:
        if not isinstance(transaction, dict):
            return "Некорректные данные транзакции"

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

    except Exception as e:
        print(f"Ошибка при форматировании транзакции: {e}")
        return f"Ошибка отображения транзакции: {e}"


@log("main.log")
def safe_filter_by_state(transactions: List[Dict[str, Any]], state: str) -> List[Dict[str, Any]]:
    """Безопасная фильтрация по статусу"""
    try:
        return filter_by_state(transactions, state)
    except Exception as e:
        print(f"Ошибка при фильтрации по статусу: {e}")
        return []


@log("main.log")
def safe_sort_by_date(transactions: List[Dict[str, Any]], ascending: bool) -> List[Dict[str, Any]]:
    """Безопасная сортировка по дате"""
    try:
        return sort_by_date(transactions, ascending)
    except Exception as e:
        print(f"Ошибка при сортировке по дате: {e}")
        return transactions  # Возвращаем исходный список в случае ошибки


@log("main.log")
def safe_process_bank_search(transactions: List[Dict[str, Any]], search_word: str) -> List[Dict[str, Any]]:
    """Безопасный поиск по слову"""
    try:
        return process_bank_search(transactions, search_word)
    except Exception as e:
        print(f"Ошибка при поиске по слову '{search_word}': {e}")
        return transactions  # Возвращаем исходный список в случае ошибки


@log("main.log")
def main() -> None:
    """Основная функция программы"""
    try:
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

        # Получение транзакций из файла
        transactions = get_transactions_from_file(file_type)

        # Проверка, что транзакции были успешно загружены
        if not transactions:
            print("Не удалось загрузить транзакции из файла. Завершение программы.")
            return

        # Фильтрация по статусу
        status = get_valid_status()
        if not status:
            print("Не удалось получить статус для фильтрации. Завершение программы.")
            return

        filtered_transactions = safe_filter_by_state(transactions, status)

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
            processed_transactions = safe_sort_by_date(processed_transactions, preferences["sort_ascending"])

        # Фильтрация по рублевым транзакциям
        if preferences["rub_only"]:
            try:
                # Преобразуем генератор в список
                processed_transactions = list(filter_by_currency(processed_transactions, "RUB"))
            except Exception as e:
                print(f"Ошибка при фильтрации по валюте: {e}")

        # Фильтрация по слову в описании
        search_word = preferences.get("search_word")
        if search_word:
            processed_transactions = safe_process_bank_search(processed_transactions, search_word)

        # Вывод результатов
        print("Распечатываю итоговый список транзакций...")
        print(f"\nВсего банковских операций в выборке: {len(processed_transactions)}\n")

        if not processed_transactions:
            print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
            return

        successful_transactions = 0
        for transaction in processed_transactions:
            try:
                if isinstance(transaction, dict):
                    formatted = format_transaction(transaction)
                    print(formatted)
                    print()
                    successful_transactions += 1
            except Exception as e:
                print(f"Ошибка при выводе транзакции: {e}")
                continue

        print(f"Успешно отображено транзакций: {successful_transactions} из {len(processed_transactions)}")

    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"Критическая ошибка в работе программы: {e}")
    finally:
        print("Работа программы завершена.")


if __name__ == "__main__":
    main()
