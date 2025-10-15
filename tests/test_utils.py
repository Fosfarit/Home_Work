import json
import os
import sys
from unittest.mock import mock_open, patch
import pytest
sys.path.append("../src")
from src.utils import read_json_file
class TestReadJsonFile:

    @patch("utils.os.path.exists")
    @patch("utils.os.path.getsize")
    def test_file_not_exists(self, mock_getsize, mock_exists):
        mock_exists.return_value = False
        result = read_json_file("/fake/path.json")
        assert result == []
        mock_exists.assert_called_once_with("/fake/path.json")
        mock_getsize.assert_not_called()

    @patch("utils.os.path.exists")
    @patch("utils.os.path.getsize")
    def test_empty_file(self, mock_getsize, mock_exists):
        mock_exists.return_value = True
        mock_getsize.return_value = 0
        result = read_json_file("/empty/file.json")
        assert result == []
        mock_exists.assert_called_once_with("/empty/file.json")
        mock_getsize.assert_called_once_with("/empty/file.json")

    @patch("utils.os.path.exists")
    @patch("utils.os.path.getsize")
    def test_valid_list_data(self, mock_getsize, mock_exists):
        mock_exists.return_value = True
        mock_getsize.return_value = 100

        mock_data = '[{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]'
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = read_json_file("/valid/file.json")

        expected = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
        assert result == expected

    @patch("utils.os.path.exists")
    @patch("utils.os.path.getsize")
    def test_not_list_data(self, mock_getsize, mock_exists):
        mock_exists.return_value = True
        mock_getsize.return_value = 100

        mock_data = '{"id": 1, "name": "test"}'
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = read_json_file("/object/file.json")

        assert result == []

    @patch("utils.os.path.exists")
    @patch("utils.os.path.getsize")
    def test_invalid_json(self, mock_getsize, mock_exists):
        mock_exists.return_value = True
        mock_getsize.return_value = 100

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("utils.json.load") as mock_json_load:
                mock_json_load.side_effect = json.JSONDecodeError("Error", "doc", 0)
                result = read_json_file("/invalid/file.json")

        assert result == []

    @patch("utils.os.path.exists")
    @patch("utils.os.path.getsize")
    def test_io_error(self, mock_getsize, mock_exists):
        mock_exists.return_value = True
        mock_getsize.return_value = 100

        with patch("builtins.open") as mock_file:
            mock_file.side_effect = IOError("Access denied")
            result = read_json_file("/protected/file.json")

        assert result == []
