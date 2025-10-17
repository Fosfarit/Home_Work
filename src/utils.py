import json
import os
from typing import Any


def read_json_file(path_to_json_file: str) -> Any | list:
    """
    Функция для чтения JSON - файла из пакета data
    """

    try:
        # Чтение и парсинг JSON файла
        with open(path_to_json_file, "r", encoding="utf-8") as pyton_file_about_the_operations:
            data = json.load(pyton_file_about_the_operations)

            # Проверка типа данных
            if not isinstance(data, list):
                print(f"Предупреждение: Данные в файле '{path_to_json_file}' не являются списком")
                return []

            return data

    except FileNotFoundError:
        print(f"Ошибка: Файл '{path_to_json_file}' не найден")
        return []

    except json.JSONDecodeError as e:
        print(f"Ошибка: Неверный формат JSON в файле '{path_to_json_file}': {e}")
        return []

    except Exception as e:
        print(f"Неожиданная ошибка при чтении файла '{path_to_json_file}': {e}")
        return []


path_to_json_file = "../data/operations.json"
result = read_json_file(path_to_json_file)
print(result)
