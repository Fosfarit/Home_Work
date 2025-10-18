import json
import logging
import os
from typing import Any, List, Union

# Настройка логирования
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

# Создаем директорию для логов, если она не существует
os.makedirs("../logs", exist_ok=True)

file_handler = logging.FileHandler("../logs/utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def read_json_file(path_to_json_file: str) -> Union[List[Any], List]:
    """
    Функция для чтения JSON-файла
    """

    try:
        # Чтение и парсинг JSON файла
        with open(path_to_json_file, "r", encoding="utf-8") as python_file_about_the_operations:
            data = json.load(python_file_about_the_operations)
        logger.info(f"Файл по пути {path_to_json_file} найден")

        # Проверка типа данных
        if not isinstance(data, list):
            logger.warning(f"Данные в файле '{path_to_json_file}' не являются списком")
            print(f"Предупреждение: Данные в файле '{path_to_json_file}' не являются списком")
            return []

        return data

    except FileNotFoundError:
        error_msg = f"Файл '{path_to_json_file}' не найден"
        logger.error(error_msg)
        print(f"Ошибка: {error_msg}")
        return []

    except json.JSONDecodeError as e:
        error_msg = f"Неверный формат JSON в файле '{path_to_json_file}': {e}"
        logger.error(error_msg)
        print(f"Ошибка: {error_msg}")
        return []

    except Exception as e:
        error_msg = f"Неожиданная ошибка при чтении файла '{path_to_json_file}': {e}"
        logger.error(error_msg)
        print(f"Ошибка: {error_msg}")
        return []


# path_to_json_file = "../data/operations.json"
# result = read_json_file(path_to_json_file)
# print(result)
