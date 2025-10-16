import json
from typing import Any
from unittest.mock import mock_open, patch

import pytest

from src.utils import read_json_file


def test_read_json_file_valid_data() -> None:
    """
    Тестирует чтение корректного JSON-файла с данными.
    """
    # Подготовка тестовых данных
    test_data = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
    test_json = json.dumps(test_data)

    # Мокаем открытие файла и проверяем результат
    with patch("builtins.open", mock_open(read_data=test_json)):
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=100):
                result = read_json_file("test_path.json")

    assert result == test_data
    assert isinstance(result, list)


def test_read_json_file_nonexistent_file() -> None:
    """
    Тестирует поведение функции при попытке чтения несуществующего файла.
    """
    with patch("os.path.exists", return_value=False):
        result = read_json_file("nonexistent.json")

    assert result == []
    assert isinstance(result, list)


def test_read_json_file_empty_file() -> None:
    """
    Тестирует поведение функции при чтении пустого файла.
    """
    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=0):
            result = read_json_file("empty.json")

    assert result == []
    assert isinstance(result, list)


def test_read_json_file_non_list_data() -> None:
    """
    Тестирует поведение функции при чтении JSON-файла с данными не в виде списка.
    """
    test_data = {"id": 1, "name": "test"}  # dict вместо list
    test_json = json.dumps(test_data)

    with patch("builtins.open", mock_open(read_data=test_json)):
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=100):
                result = read_json_file("test_path.json")

    assert result == []
    assert isinstance(result, list)


def test_read_json_file_invalid_json() -> None:
    """
    Тестирует поведение функции при чтении файла с некорректным JSON.
    """
    invalid_json = "{invalid json}"

    with patch("builtins.open", mock_open(read_data=invalid_json)):
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=100):
                # Ожидаем исключение при парсинге некорректного JSON
                with pytest.raises(json.JSONDecodeError):
                    read_json_file("invalid.json")


def test_read_json_file_encoding() -> None:
    """
    Тестирует корректность работы с кодировкой UTF-8.
    """
    test_data = [{"name": "тест", "description": "Описание с кириллицей"}]
    test_json = json.dumps(test_data, ensure_ascii=False)

    with patch("builtins.open", mock_open(read_data=test_json)) as mock_file:
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=100):
                result = read_json_file("unicode.json")

        # Проверяем, что файл открыт с правильной кодировкой
        mock_file.assert_called_with("unicode.json", "r", encoding="utf-8")

    assert result == test_data


def test_read_json_file_return_type_annotation() -> None:
    """
    Тестирует соответствие аннотации типа возвращаемого значения.
    """
    # Проверяем аннотацию типа функции
    return_annotation = read_json_file.__annotations__.get("return")
    assert return_annotation in (Any | list, Any, list)


def test_read_json_file_parameter_type_annotation() -> None:
    """
    Тестирует аннотацию типа параметра функции.
    """
    # Проверяем аннотацию типа параметра
    param_annotation = read_json_file.__annotations__.get("path_to_json_file")
    assert param_annotation == str


@pytest.mark.parametrize(
    "file_size,expected_empty",
    [
        (0, True),  # Пустой файл
        (1, False),  # Непустой файл
    ],
)
def test_read_json_file_size_cases(file_size: int, expected_empty: bool) -> None:
    """
    Параметризованный тест для различных случаев размера файла.
    """
    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=file_size):
            if expected_empty:
                result = read_json_file("test.json")
                assert result == []
            else:
                # Для непустого файла нужны дополнительные моки
                test_data = [{"test": "data"}]
                test_json = json.dumps(test_data)
                with patch("builtins.open", mock_open(read_data=test_json)):
                    result = read_json_file("test.json")
                    assert result == test_data


def test_read_json_file_integration(tmp_path: pytest.TempPathFactory) -> None:
    """
    Интеграционный тест с созданием временного файла.
    """
    # Создаем временный файл с тестовыми данными
    test_data = [{"id": 1, "operation": "test"}]
    temp_file = tmp_path / "test_operations.json"
    temp_file.write_text(json.dumps(test_data), encoding="utf-8")

    # Тестируем функцию с реальным файлом
    result = read_json_file(str(temp_file))

    assert result == test_data
    assert isinstance(result, list)
