import json
# import os
# from typing import Any
from unittest.mock import mock_open, patch

from src.utils import read_json_file

# import pytest



def test_read_json_file_success():
    """Тест успешного чтения JSON файла со списком"""
    mock_data = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result = read_json_file("test_path.json")

        assert result == mock_data


def test_read_json_file_not_list():
    """Тест чтения JSON файла с данными не в виде списка"""
    mock_data = {"id": 1, "name": "test"}  # dict вместо list

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
        patch("builtins.print") as mock_print,
    ):
        result = read_json_file("test_path.json")

        assert result == []
        mock_print.assert_called_once_with("Предупреждение: Данные в файле 'test_path.json' не являются списком")


def test_read_json_file_not_found():
    """Тест случая когда файл не существует"""
    with patch("os.path.exists", return_value=False), patch("builtins.print") as mock_print:
        result = read_json_file("nonexistent.json")

        assert result == []
        mock_print.assert_not_called()  # FileNotFoundError не должен вызывать print


def test_read_json_file_empty():
    """Тест случая когда файл пустой"""
    with patch("os.path.exists", return_value=True), patch("os.path.getsize", return_value=0):
        result = read_json_file("empty.json")

        assert result == []


def test_read_json_file_json_decode_error():
    """Тест случая с ошибкой декодирования JSON"""
    invalid_json = "{invalid json}"

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=invalid_json)),
        patch("builtins.print") as mock_print,
    ):
        result = read_json_file("invalid.json")

        assert result == []
        mock_print.assert_called_once()
        assert "Неверный формат JSON" in mock_print.call_args[0][0]


def test_read_json_file_general_exception():
    """Тест обработки общего исключения"""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", side_effect=Exception("Unexpected error")),
        patch("builtins.print") as mock_print,
    ):
        result = read_json_file("error.json")

        assert result == []
        mock_print.assert_called_once()
        assert "Неожиданная ошибка" in mock_print.call_args[0][0]


def test_read_json_file_file_not_found_exception():
    """Тест явного исключения FileNotFoundError"""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", side_effect=FileNotFoundError),
        patch("builtins.print") as mock_print,
    ):
        result = read_json_file("missing.json")

        assert result == []
        mock_print.assert_called_once_with("Ошибка: Файл 'missing.json' не найден")


def test_read_json_file_with_nested_structure():
    """Тест с более сложной структурой данных"""
    mock_data = [
        {"id": 1, "operation": "transfer", "amount": 1000, "details": {"from": "acc1", "to": "acc2"}},
        {"id": 2, "operation": "withdrawal", "amount": 500},
    ]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result = read_json_file("complex_data.json")

        assert result == mock_data
        assert len(result) == 2
        assert result[0]["operation"] == "transfer"
        assert result[1]["amount"] == 500
