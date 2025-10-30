import re
from typing import List, Dict


def process_bank_search(data: List[Dict], search: str) -> List[Dict]:
    """
    Фильтрует список банковских операций по наличию строки поиска в описании.

    Args:
        data: Список словарей с данными о банковских операциях
        search: Строка для поиска в описании операций

    Returns:
        Список словарей, у которых в описании есть искомая строка
    """
    if not search:
        return data

    try:
        # Создаем регулярное выражение для поиска (регистронезависимое)
        pattern = re.compile(search, re.IGNORECASE)

        # Фильтруем операции, где описание содержит искомую строку
        filtered_data = [
            operation for operation in data
            if operation.get('description') and pattern.search(operation['description'])
        ]

        return filtered_data

    except re.error:
        # В случае ошибки в регулярном выражении возвращаем пустой список
        return []


def process_bank_operations_advanced(data: list[dict], categories: list, case_sensitive: bool = False) -> dict:
    """
    Функция считает количество операций.
    """
    category_count = {category: 0 for category in categories}

    for operation in data:
        description = operation.get('description')
        if not description:
            continue

        if not case_sensitive:
            description = description.lower()
            matched_categories = [cat for cat in categories if cat.lower() == description]
        else:
            matched_categories = [cat for cat in categories if cat == description]

        for category in matched_categories:
            category_count[category] += 1

    return category_count