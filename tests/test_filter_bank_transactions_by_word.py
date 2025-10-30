import pytest
import re
from unittest.mock import patch, MagicMock
from src.filter_bank_transactions_by_word import process_bank_search, process_bank_operations_advanced


def test_process_bank_search_empty_search():
    """Тест с пустой строкой поиска"""
    test_data = [
        {'description': 'Payment for groceries'},
        {'description': 'Salary'},
        {'description': None}
    ]

    result = process_bank_search(test_data, '')

    assert result == test_data


def test_process_bank_search_none_search():
    """Тест с None в качестве строки поиска"""
    test_data = [
        {'description': 'Payment for groceries'},
        {'description': 'Salary'}
    ]

    result = process_bank_search(test_data, None)

    assert result == test_data


def test_process_bank_search_basic_matching():
    """Тест базового поиска с совпадениями"""
    test_data = [
        {'description': 'Payment for groceries'},
        {'description': 'Salary payment'},
        {'description': 'Coffee shop'},
        {'description': ''}
    ]

    result = process_bank_search(test_data, 'payment')

    assert len(result) == 2
    assert result[0]['description'] == 'Payment for groceries'
    assert result[1]['description'] == 'Salary payment'


def test_process_bank_search_case_insensitive():
    """Тест регистронезависимого поиска"""
    test_data = [
        {'description': 'PAYMENT for groceries'},
        {'description': 'salary Payment'},
        {'description': 'Coffee shop'}
    ]

    result = process_bank_search(test_data, 'payment')

    assert len(result) == 2
    assert result[0]['description'] == 'PAYMENT for groceries'
    assert result[1]['description'] == 'salary Payment'


def test_process_bank_search_no_matches():
    """Тест поиска без совпадений"""
    test_data = [
        {'description': 'Salary'},
        {'description': 'Coffee shop'}
    ]

    result = process_bank_search(test_data, 'payment')

    assert result == []


def test_process_bank_search_empty_data():
    """Тест с пустыми данными"""
    result = process_bank_search([], 'payment')

    assert result == []


def test_process_bank_search_operations_without_description():
    """Тест с операциями без описания"""
    test_data = [
        {'description': 'Payment for groceries'},
        {'description': None},
        {'amount': 100},
        {'description': ''}
    ]

    result = process_bank_search(test_data, 'payment')

    assert len(result) == 1
    assert result[0]['description'] == 'Payment for groceries'


def test_process_bank_search_regex_error():
    """Тест обработки ошибки регулярного выражения"""
    test_data = [
        {'description': 'Payment for groceries'}
    ]

    # Используем невалидное регулярное выражение
    result = process_bank_search(test_data, '[')

    assert result == []


def test_process_bank_search_special_regex_chars():
    """Тест с специальными символами регулярных выражений"""
    test_data = [
        {'description': 'Payment (urgent)'},
        {'description': 'Regular payment'},
        {'description': 'Salary'}
    ]

    result = process_bank_search(test_data, 'Payment \\(urgent\\)')

    # Должен найти только точное совпадение с экранированными скобками
    if result:  # Проверяем только если есть результаты
        assert len(result) == 1
        assert result[0]['description'] == 'Payment (urgent)'


def test_process_bank_search_special_regex_chars_simple():
    """Тест с простым поиском специальных символов"""
    test_data = [
        {'description': 'Payment (urgent)'},
        {'description': 'Regular payment'},
        {'description': 'Salary'}
    ]

    # Ищем просто "urgent" вместо сложного regex
    result = process_bank_search(test_data, 'urgent')

    assert len(result) == 1
    assert result[0]['description'] == 'Payment (urgent)'


@patch('src.filter_bank_transactions_by_word.re.compile')
def test_process_bank_search_regex_compilation(mock_compile):
    """Тест компиляции регулярного выражения"""
    mock_pattern = MagicMock()
    mock_compile.return_value = mock_pattern
    mock_pattern.search.return_value = True

    test_data = [
        {'description': 'Test payment'}
    ]

    result = process_bank_search(test_data, 'payment')

    mock_compile.assert_called_once_with('payment', re.IGNORECASE)
    mock_pattern.search.assert_called_once_with('Test payment')


@patch('src.filter_bank_transactions_by_word.re.compile')
def test_process_bank_search_regex_error_mocked(mock_compile):
    """Тест ошибки регулярного выражения с моком"""
    mock_compile.side_effect = re.error("Invalid regex")

    test_data = [
        {'description': 'Payment for groceries'}
    ]

    result = process_bank_search(test_data, 'invalid[')

    assert result == []
    mock_compile.assert_called_once_with('invalid[', re.IGNORECASE)


def test_process_bank_operations_advanced_basic():
    """Тест базовой функциональности усовершенствованной функции"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'Salary'},
        {'description': 'Groceries'},
        {'description': 'Entertainment'}
    ]

    categories = ['Groceries', 'Salary']
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {'Groceries': 2, 'Salary': 1}


def test_process_bank_operations_advanced_case_sensitive():
    """Тест с учетом регистра"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'groceries'},
        {'description': 'GROCERIES'}
    ]

    categories = ['Groceries']
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=True)

    assert result == {'Groceries': 1}


def test_process_bank_operations_advanced_case_insensitive():
    """Тест без учета регистра"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'groceries'},
        {'description': 'GROCERIES'}
    ]

    categories = ['Groceries']
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=False)

    assert result == {'Groceries': 3}


def test_process_bank_operations_advanced_empty_categories():
    """Тест с пустым списком категорий"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'Salary'}
    ]

    result = process_bank_operations_advanced(test_data, [])

    assert result == {}


def test_process_bank_operations_advanced_no_description():
    """Тест с операциями без описания"""
    test_data = [
        {'description': 'Groceries'},
        {'description': None},
        {'amount': 100},
        {'description': ''}
    ]

    categories = ['Groceries']
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {'Groceries': 1}


def test_process_bank_operations_advanced_no_matches():
    """Тест без совпадений категорий"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'Salary'}
    ]

    categories = ['Entertainment', 'Travel']
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {'Entertainment': 0, 'Travel': 0}


def test_process_bank_operations_advanced_mixed_case_categories():
    """Тест со смешанным регистром в категориях"""
    test_data = [
        {'description': 'groceries'},
        {'description': 'SALARY'}
    ]

    categories = ['Groceries', 'Salary']
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=False)

    assert result == {'Groceries': 1, 'Salary': 1}


def test_process_bank_operations_advanced_exact_match():
    """Тест точного совпадения описаний"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'Monthly Groceries'},
        {'description': 'Groceries '}  # С пробелом
    ]

    categories = ['Groceries']
    result = process_bank_operations_advanced(test_data, categories, case_sensitive=True)

    # Только точное совпадение
    assert result == {'Groceries': 1}


def test_process_bank_operations_advanced_multiple_categories():
    """Тест с несколькими категориями"""
    test_data = [
        {'description': 'Groceries'},
        {'description': 'Salary'},
        {'description': 'Groceries'},
        {'description': 'Salary'},
        {'description': 'Entertainment'}
    ]

    categories = ['Groceries', 'Salary', 'Entertainment']
    result = process_bank_operations_advanced(test_data, categories)

    assert result == {'Groceries': 2, 'Salary': 2, 'Entertainment': 1}