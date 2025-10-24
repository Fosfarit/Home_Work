import json
from typing import Any, Dict, List
from unittest.mock import mock_open, patch

from src.utils import read_json_file


def test_read_json_file_success() -> None:
    """Тест успешного чтения JSON файла со списком"""
    mock_data: List[Dict[str, Any]] = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result: List[Dict[str, Any]] = read_json_file("test_path.json")
        assert result == mock_data


def test_read_json_file_not_list() -> None:
    """Тест чтения JSON файла с данными не в виде списка"""
    mock_data: Dict[str, Any] = {"id": 1, "name": "test"}  # dict вместо list

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
        patch("builtins.print") as mock_print,
    ):
        result: List[Any] = read_json_file("test_path.json")
        assert result == []
        mock_print.assert_called_once_with("Предупреждение: Данные в файле 'test_path.json' не являются списком")


def test_read_json_file_not_found() -> None:
    """Тест случая когда файл не существует"""
    with (
        patch("os.path.exists", return_value=False),
        patch("builtins.print") as mock_print,
    ):
        result: List[Any] = read_json_file("nonexistent.json")
        assert result == []
        mock_print.assert_called_once_with("Ошибка: Файл 'nonexistent.json' не найден")


def test_read_json_file_empty() -> None:
    """Тест случая когда файл пустой"""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=0),
        patch("builtins.open", mock_open(read_data="")),
    ):
        result: List[Any] = read_json_file("empty.json")
        assert result == []


def test_read_json_file_json_decode_error() -> None:
    """Тест случая с ошибкой декодирования JSON"""
    invalid_json: str = "{invalid json}"

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=invalid_json)),
        patch("builtins.print") as mock_print,
    ):
        result: List[Any] = read_json_file("invalid.json")
        assert result == []
        mock_print.assert_called_once()
        assert "Неверный формат JSON" in mock_print.call_args[0][0]


def test_read_json_file_general_exception() -> None:
    """Тест обработки общего исключения"""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", side_effect=Exception("Unexpected error")),
        patch("builtins.print") as mock_print,
    ):
        result: List[Any] = read_json_file("error.json")
        assert result == []
        mock_print.assert_called_once()
        assert "Неожиданная ошибка" in mock_print.call_args[0][0]


def test_read_json_file_file_not_found_exception() -> None:
    """Тест явного исключения FileNotFoundError"""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", side_effect=FileNotFoundError("File not found")),
        patch("builtins.print") as mock_print,
    ):
        result: List[Any] = read_json_file("missing.json")
        assert result == []
        mock_print.assert_called_once_with("Ошибка: Файл 'missing.json' не найден")


def test_read_json_file_with_nested_structure() -> None:
    """Тест с более сложной структурой данных"""
    mock_data: List[Dict[str, Any]] = [
        {
            "id": 1,
            "operation": "transfer",
            "amount": 1000,
            "details": {"from": "acc1", "to": "acc2"},
        },
        {"id": 2, "operation": "withdrawal", "amount": 500},
    ]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result: List[Dict[str, Any]] = read_json_file("complex_data.json")
        assert result == mock_data
        assert len(result) == 2
        assert result[0]["operation"] == "transfer"
        assert result[1]["amount"] == 500


def test_read_json_file_logging_info() -> None:
    """Тест логирования успешного чтения файла"""
    mock_data: List[Dict[str, str]] = [{"test": "data"}]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
        patch("src.utils.logger") as mock_logger,
    ):
        result: List[Dict[str, str]] = read_json_file("test.json")
        assert result == mock_data
        mock_logger.info.assert_called_once_with("Файл по пути test.json найден")


def test_read_json_file_logging_warning() -> None:
    """Тест логирования предупреждения при данных не в виде списка"""
    mock_data: Dict[str, str] = {"test": "data"}

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
        patch("src.utils.logger") as mock_logger,
    ):
        result: List[Any] = read_json_file("test.json")
        assert result == []
        mock_logger.warning.assert_called_once_with("Данные в файле 'test.json' не являются списком")


def test_read_json_file_logging_error_file_not_found() -> None:
    """Тест логирования ошибки когда файл не найден"""
    with (
        patch("os.path.exists", return_value=False),
        patch("src.utils.logger") as mock_logger,
    ):
        result: List[Any] = read_json_file("nonexistent.json")
        assert result == []
        mock_logger.error.assert_called_once_with("Файл 'nonexistent.json' не найден")


def test_read_json_file_logging_error_json_decode() -> None:
    """Тест логирования ошибки декодирования JSON"""
    invalid_json: str = "{invalid json}"

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=invalid_json)),
        patch("src.utils.logger") as mock_logger,
    ):
        result: List[Any] = read_json_file("invalid.json")
        assert result == []
        mock_logger.error.assert_called_once()
        assert "Неверный формат JSON" in mock_logger.error.call_args[0][0]


def test_read_json_file_logging_error_general() -> None:
    """Тест логирования общей ошибки"""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", side_effect=Exception("Unexpected error")),
        patch("src.utils.logger") as mock_logger,
    ):
        result: List[Any] = read_json_file("error.json")
        assert result == []
        mock_logger.error.assert_called_once()
        assert "Неожиданная ошибка" in mock_logger.error.call_args[0][0]


# def test_read_json_file_encoding_utf8(mock_file=None) -> None:
#     """Тест что файл открывается с правильной кодировкой"""
#     mock_data: List[Dict[str, str]] = [{"test": "данные с кириллицей"}]
#
#     with (
#         patch("os.path.exists", return_value=True),
#         patch("os.path.getsize", return_value=100),
#         patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
#     ):
#         result: List[Dict[str, str]] = read_json_file("unicode.json")
#         assert result == mock_data
#         # Проверяем что файл открыт с кодировкой utf-8
#         mock_file.assert_called_once_with("unicode.json", "r", encoding="utf-8")


def test_read_json_file_empty_list() -> None:
    """Тест чтения файла с пустым списком"""
    mock_data: List[Any] = []

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result: List[Any] = read_json_file("empty_list.json")
        assert result == []
        assert isinstance(result, list)


def test_read_json_file_large_file() -> None:
    """Тест чтения большого файла"""
    mock_data: List[Dict[str, Any]] = [{"id": i, "value": f"test_{i}"} for i in range(1000)]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=50000),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result: List[Dict[str, Any]] = read_json_file("large.json")
        assert result == mock_data
        assert len(result) == 1000


def test_read_json_file_special_characters() -> None:
    """Тест чтения файла со специальными символами"""
    mock_data: List[Dict[str, str]] = [{"text": "Line 1\nLine 2\tTab"}, {"quotes": "\"test\" 'single'"}]

    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.getsize", return_value=100),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
    ):
        result: List[Dict[str, str]] = read_json_file("special_chars.json")
        assert result == mock_data
