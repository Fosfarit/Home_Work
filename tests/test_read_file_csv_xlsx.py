import os
# Импортируем тестируемые функции
import sys
from unittest.mock import Mock, patch

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from read_files_csv_and_xlsx import read_CSV_file, read_xlsx_file


def test_read_CSV_file_success() -> None:
    """Тест успешного чтения CSV файла"""
    # Создаем мок данных
    mock_data = [{"id": 1, "amount": 100, "date": "2023-01-01"}, {"id": 2, "amount": 200, "date": "2023-01-02"}]

    mock_df = Mock()
    mock_df.to_dict.return_value = mock_data

    # Патчим pd.read_csv
    with patch("pandas.read_csv", return_value=mock_df) as mock_read_csv:
        result = read_CSV_file("test.csv")

        # Проверяем вызовы
        mock_read_csv.assert_called_once_with("test.csv", delimiter=";")
        mock_df.to_dict.assert_called_once_with("records")

        # Проверяем результат
        assert result == mock_data


def test_read_CSV_file_file_not_found() -> None:
    """Тест обработки FileNotFoundError для CSV файла"""
    with patch("pandas.read_csv", side_effect=FileNotFoundError("File not found")) as mock_read_csv:
        with pytest.raises(FileNotFoundError, match="Файл 'nonexistent.csv' не найден"):
            read_CSV_file("nonexistent.csv")


def test_read_CSV_file_type_error() -> None:
    """Тест проверки типа аргумента для CSV функции"""
    with pytest.raises(TypeError, match="Путь к файлу должен быть строкой"):
        read_CSV_file(123)


def test_read_xlsx_file_success() -> None:
    """Тест успешного чтения XLSX файла"""
    # Создаем мок данных
    mock_data = [{"id": 1, "amount": 150, "date": "2023-01-01"}, {"id": 2, "amount": 250, "date": "2023-01-02"}]

    mock_df = Mock()
    mock_df.to_dict.return_value = mock_data

    # Патчим pd.read_excel
    with patch("pandas.read_excel", return_value=mock_df) as mock_read_excel:
        result = read_xlsx_file("test.xlsx")

        # Проверяем вызовы
        mock_read_excel.assert_called_once_with("test.xlsx")
        mock_df.to_dict.assert_called_once_with("records")

        # Проверяем результат
        assert result == mock_data


def test_read_xlsx_file_file_not_found() -> None:
    """Тест обработки FileNotFoundError для XLSX файла"""
    with patch("pandas.read_excel", side_effect=FileNotFoundError("File not found")) as mock_read_excel:
        with pytest.raises(FileNotFoundError, match="Файл 'nonexistent.xlsx' не найден"):
            read_xlsx_file("nonexistent.xlsx")


def test_read_xlsx_file_type_error() -> None:
    """Тест проверки типа аргумента для XLSX функции"""
    with pytest.raises(TypeError, match="Путь к файлу должен быть строкой"):
        read_xlsx_file(456)


def test_read_CSV_file_pandas_exception() -> None:
    """Тест обработки других исключений pandas для CSV"""
    with patch("pandas.read_csv", side_effect=Exception("Pandas error")) as mock_read_csv:
        with pytest.raises(Exception, match="Pandas error"):
            read_CSV_file("test.csv")


def test_read_xlsx_file_pandas_exception() -> None:
    """Тест обработки других исключений pandas для XLSX"""
    with patch("pandas.read_excel", side_effect=Exception("Pandas error")) as mock_read_excel:
        with pytest.raises(Exception, match="Pandas error"):
            read_xlsx_file("test.xlsx")


def test_read_CSV_file_empty_file() -> None:
    """Тест чтения пустого CSV файла"""
    mock_df = Mock()
    mock_df.to_dict.return_value = []

    with patch("pandas.read_csv", return_value=mock_df) as mock_read_csv:
        result = read_CSV_file("empty.csv")

        assert result == []
        mock_read_csv.assert_called_once_with("empty.csv", delimiter=";")


def test_read_xlsx_file_empty_file() -> None:
    """Тест чтения пустого XLSX файла"""
    mock_df = Mock()
    mock_df.to_dict.return_value = []

    with patch("pandas.read_excel", return_value=mock_df) as mock_read_excel:
        result = read_xlsx_file("empty.xlsx")

        assert result == []
        mock_read_excel.assert_called_once_with("empty.xlsx")


def test_read_CSV_file_with_special_characters() -> None:
    """Тест чтения CSV файла с путем, содержащим специальные символы"""
    mock_df = Mock()
    mock_df.to_dict.return_value = [{"test": "data"}]

    with patch("pandas.read_csv", return_value=mock_df) as mock_read_csv:
        result = read_CSV_file("path/with spaces/and-special_chars.csv")

        mock_read_csv.assert_called_once_with("path/with spaces/and-special_chars.csv", delimiter=";")
        assert result == [{"test": "data"}]


def test_read_xlsx_file_with_special_characters() -> None:
    """Тест чтения XLSX файла с путем, содержащим специальные символы"""
    mock_df = Mock()
    mock_df.to_dict.return_value = [{"test": "data"}]

    with patch("pandas.read_excel", return_value=mock_df) as mock_read_excel:
        result = read_xlsx_file("path/with spaces/and-special_chars.xlsx")

        mock_read_excel.assert_called_once_with("path/with spaces/and-special_chars.xlsx")
        assert result == [{"test": "data"}]
