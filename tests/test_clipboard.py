import pytest
from unittest.mock import patch, MagicMock

from geoff.clipboard import copy_to_clipboard


class TestCopyToClipboard:
    def test_copy_success(self):
        with patch("geoff.clipboard.pyperclip.copy") as mock_copy:
            result = copy_to_clipboard("test prompt")
            mock_copy.assert_called_once_with("test prompt")
            assert result is True

    def test_copy_returns_true_on_exception(self):
        with patch(
            "geoff.clipboard.pyperclip.copy", side_effect=Exception("Clipboard error")
        ):
            result = copy_to_clipboard("test prompt")
            assert result is False

    def test_copy_empty_string(self):
        with patch("geoff.clipboard.pyperclip.copy") as mock_copy:
            result = copy_to_clipboard("")
            mock_copy.assert_called_once_with("")
            assert result is True

    def test_copy_multiline_string(self):
        multiline = "line1\nline2\nline3"
        with patch("geoff.clipboard.pyperclip.copy") as mock_copy:
            result = copy_to_clipboard(multiline)
            mock_copy.assert_called_once_with(multiline)
            assert result is True
