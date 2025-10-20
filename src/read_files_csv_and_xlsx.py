from typing import Any, Dict, List

import pandas as pd


def read_CSV_file(transactions_csv: str) -> List[Dict[str, Any]]:
    """Функция прочитывает файл в формате csv и возвращает список словарей с транзакциями"""
    if not isinstance(transactions_csv, str):
        raise TypeError("Путь к файлу должен быть строкой")

    try:
        file_csv = pd.read_csv(transactions_csv, delimiter=";")
        return file_csv.to_dict("records")

    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{transactions_csv}' не найден")


# transactions_csv = "../data/transactions.csv"
# print(read_CSV_file(transactions_csv))


def read_xlsx_file(transactions_xlsx: str) -> List[Dict[str, Any]]:
    """Функция прочитывает файл в формате xlsx и возвращает список словарей с транзакциями"""
    if not isinstance(transactions_xlsx, str):
        raise TypeError("Путь к файлу должен быть строкой")

    try:
        file_excel = pd.read_excel(transactions_xlsx)
        return file_excel.to_dict("records")

    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{transactions_xlsx}' не найден")


# transactions_xlsx = "../data/transactions_excel.xlsx"
# print(read_xlsx_file(transactions_xlsx))
