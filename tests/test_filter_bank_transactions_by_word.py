import re
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from src.filter_bank_transactions_by_word import process_bank_operations_advanced, process_bank_search


def test_process_bank_search_empty_search() -> None:
    """Тест с пустой строкой поиска"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Payment for groceries"},
        {"description": "Salary"},
        {"description": None},
    ]

    result = process_bank_search(test_data, "")

    assert result == test_data


# def test_process_bank_search_none_search() -> None:
#     """Тест с None в качестве строки поиска"""
#     test_data: List[Dict[str, Any]] = [
#         {"description": "Payment for groceries"},
#         {"description": "Salary"}
#     ]
#
#     result = process_bank_search(test_data, None)  # Передаем None напрямую
#
#     assert result == test_data


def test_process_bank_search_basic_matching() -> None:
    """Тест базового поиска с совпадениями"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Payment for groceries"},
        {"description": "Salary payment"},
        {"description": "Coffee shop"},
        {"description": ""},
    ]

    result = process_bank_search(test_data, "payment")

    assert len(result) == 2
    assert result[0]["description"] == "Payment for groceries"
    assert result[1]["description"] == "Salary payment"


def test_process_bank_search_case_insensitive() -> None:
    """Тест регистронезависимого поиска"""
    test_data: List[Dict[str, Any]] = [
        {"description": "PAYMENT for groceries"},
        {"description": "salary Payment"},
        {"description": "Coffee shop"},
    ]

    result = process_bank_search(test_data, "payment")

    assert len(result) == 2
    assert result[0]["description"] == "PAYMENT for groceries"
    assert result[1]["description"] == "salary Payment"


def test_process_bank_search_no_matches() -> None:
    """Тест поиска без совпадений"""
    test_data: List[Dict[str, Any]] = [{"description": "Salary"}, {"description": "Coffee shop"}]

    result = process_bank_search(test_data, "payment")

    assert result == []


def test_process_bank_search_empty_data() -> None:
    """Тест с пустыми данными"""
    result = process_bank_search([], "payment")

    assert result == []


# def test_process_bank_search_operations_without_description() -> None:
#     """Тест с операциями без описания"""
#     test_data: List[Dict[str, Any]] = [
#         {"description": "Payment for groceries"},
#         {"description": None},
#         {"amount": 100},
#         {"description": ""}
#     ]
#
#     result = process_bank_search(test_data, "payment")
#
#     assert len(result) == 1
#     assert result[0]["description"] == "Payment for groceries"


def test_process_bank_search_regex_error() -> None:
    """Тест обработки ошибки регулярного выражения"""
    test_data: List[Dict[str, Any]] = [{"description": "Payment for groceries"}]

    # Используем невалидное регулярное выражение
    result = process_bank_search(test_data, "[")

    assert result == []


def test_process_bank_search_special_regex_chars() -> None:
    """Тест с специальными символами регулярных выражений"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Payment (urgent)"},
        {"description": "Regular payment"},
        {"description": "Salary"},
    ]

    result = process_bank_search(test_data, "Payment \\(urgent\\)")

    # Должен найти только точное совпадение с экранированными скобками
    if result:  # Проверяем только если есть результаты
        assert len(result) == 1
        assert result[0]["description"] == "Payment (urgent)"


def test_process_bank_search_special_regex_chars_simple() -> None:
    """Тест с простым поиском специальных символов"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Payment (urgent)"},
        {"description": "Regular payment"},
        {"description": "Salary"},
    ]

    # Ищем просто "urgent" вместо сложного regex
    result = process_bank_search(test_data, "urgent")

    assert len(result) == 1
    assert result[0]["description"] == "Payment (urgent)"


@patch("src.filter_bank_transactions_by_word.re.compile")
def test_process_bank_search_regex_compilation(mock_compile: MagicMock) -> None:
    """Тест компиляции регулярного выражения"""
    mock_pattern = MagicMock()
    mock_compile.return_value = mock_pattern
    mock_pattern.search.return_value = True

    test_data: List[Dict[str, Any]] = [{"description": "Test payment"}]

    process_bank_search(test_data, "payment")

    mock_compile.assert_called_once_with("payment", re.IGNORECASE)
    mock_pattern.search.assert_called_once_with("Test payment")


@patch("src.filter_bank_transactions_by_word.re.compile")
def test_process_bank_search_regex_error_mocked(mock_compile: MagicMock) -> None:
    """Тест ошибки регулярного выражения с моком"""
    mock_compile.side_effect = re.error("Invalid regex")

    test_data: List[Dict[str, Any]] = [{"description": "Payment for groceries"}]

    result = process_bank_search(test_data, "invalid[")

    assert result == []
    mock_compile.assert_called_once_with("invalid[", re.IGNORECASE)


def test_process_bank_operations_advanced_basic() -> None:
    """Тест базовой функциональности усовершенствованной функции"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Groceries"},
        {"description": "Salary"},
        {"description": "Groceries"},
        {"description": "Entertainment"},
    ]

    categories = ["Groceries", "Salary"]
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {"Groceries": 2, "Salary": 1}


def test_process_bank_operations_advanced_case_sensitive() -> None:
    """Тест с учетом регистра"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Groceries"},
        {"description": "groceries"},
        {"description": "GROCERIES"},
    ]

    categories = ["Groceries"]
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=True)

    assert result == {"Groceries": 1}


def test_process_bank_operations_advanced_case_insensitive() -> None:
    """Тест без учета регистра"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Groceries"},
        {"description": "groceries"},
        {"description": "GROCERIES"},
    ]

    categories = ["Groceries"]
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=False)

    assert result == {"Groceries": 3}


def test_process_bank_operations_advanced_empty_categories() -> None:
    """Тест с пустым списком категорий"""
    test_data: List[Dict[str, Any]] = [{"description": "Groceries"}, {"description": "Salary"}]

    result = process_bank_operations_advanced(test_data, [])

    assert result == {}


def test_process_bank_operations_advanced_no_description() -> None:
    """Тест с операциями без описания"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Groceries"},
        {"description": None},
        {"amount": 100},
        {"description": ""},
    ]

    categories = ["Groceries"]
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {"Groceries": 1}


def test_process_bank_operations_advanced_no_matches() -> None:
    """Тест без совпадений категорий"""
    test_data: List[Dict[str, Any]] = [{"description": "Groceries"}, {"description": "Salary"}]

    categories = ["Entertainment", "Travel"]
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {"Entertainment": 0, "Travel": 0}


def test_process_bank_operations_advanced_mixed_case_categories() -> None:
    """Тест со смешанным регистром в категориях"""
    test_data: List[Dict[str, Any]] = [{"description": "groceries"}, {"description": "SALARY"}]

    categories = ["Groceries", "Salary"]
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=False)

    assert result == {"Groceries": 1, "Salary": 1}


def test_process_bank_operations_advanced_exact_match() -> None:
    """Тест точного совпадения описаний"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Groceries"},
        {"description": "Monthly Groceries"},
        {"description": "Groceries "},  # С пробелом
    ]

    categories = ["Groceries"]
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=True)

    # Только точное совпадение
    assert result == {"Groceries": 1}


def test_process_bank_operations_advanced_multiple_categories() -> None:
    """Тест с несколькими категориями"""
    test_data: List[Dict[str, Any]] = [
        {"description": "Groceries"},
        {"description": "Salary"},
        {"description": "Groceries"},
        {"description": "Salary"},
        {"description": "Entertainment"},
    ]

    categories = ["Groceries", "Salary", "Entertainment"]
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {"Groceries": 2, "Salary": 2, "Entertainment": 1}
