import json
import os
from typing import Any


def read_json_file(path_to_json_file: str) -> Any | list:
    """
    Функция для чтения JSON - файла из пакета data
    """
    if not os.path.exists(path_to_json_file) or os.path.getsize(path_to_json_file) == 0:
        return []
    with open(path_to_json_file, "r", encoding="utf-8") as pyton_file_about_the_operations:
        data = json.load(pyton_file_about_the_operations)
        if type(data) is not list:
            return []
        return data
