import pytest
from unittest.mock import patch, MagicMock, mock_open

from geoff.clipboard import (
    ClipboardError,
    copy_to_clipboard,
    _is_wsl,
    _copy_with_clip_exe,
    _get_clip_exe_path,
)


class TestIsWSL:
    def test_wsl_distro_name_detected(self):
        with patch.dict("os.environ", {"WSL_DISTRO_NAME": "Ubuntu"}, clear=True):
            assert _is_wsl() is True

    def test_wslenv_detected(self):
        with patch.dict("os.environ", {"WSLENV": "PATH/l"}, clear=True):
            assert _is_wsl() is True

    def test_proc_version_microsoft(self):
        with patch(
            "builtins.open",
            mock_open(read_data="Linux version 5.15.0-microsoft-standard"),
        ):
            with patch.dict("os.environ", {}, clear=True):
                assert _is_wsl() is True

    def test_not_wsl(self):
        with patch(
            "builtins.open", mock_open(read_data="Linux version 5.15.0-generic")
        ):
            with patch.dict("os.environ", {}, clear=True):
                assert _is_wsl() is False


class TestGetClipExePath:
    def test_found(self):
        with patch("os.path.exists", side_effect=lambda p: "System32" in p):
            assert _get_clip_exe_path() == "/mnt/c/Windows/System32/clip.exe"

    def test_not_found(self):
        with patch("os.path.exists", return_value=False):
            assert _get_clip_exe_path() is None


class TestCopyWithClipExe:
    def test_success(self):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")

        with patch("subprocess.Popen", return_value=mock_process):
            with patch(
                "geoff.clipboard._get_clip_exe_path",
                return_value="/mnt/c/Windows/System32/clip.exe",
            ):
                _copy_with_clip_exe("test text")

        mock_process.communicate.assert_called_once_with(b"test text")

    def test_not_found(self):
        with patch("geoff.clipboard._get_clip_exe_path", return_value=None):
            with pytest.raises(RuntimeError, match="clip.exe not found"):
                _copy_with_clip_exe("test text")

    def test_failure(self):
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"error")

        with patch("subprocess.Popen", return_value=mock_process):
            with patch(
                "geoff.clipboard._get_clip_exe_path",
                return_value="/mnt/c/Windows/System32/clip.exe",
            ):
                with pytest.raises(RuntimeError, match="clip.exe failed"):
                    _copy_with_clip_exe("test text")


class TestCopyToClipboard:
    def test_wsl_success(self):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")

        with patch("geoff.clipboard._is_wsl", return_value=True):
            with patch("subprocess.Popen", return_value=mock_process):
                with patch(
                    "geoff.clipboard._get_clip_exe_path",
                    return_value="/mnt/c/Windows/System32/clip.exe",
                ):
                    copy_to_clipboard("test")

        mock_process.communicate.assert_called_once_with(b"test")

    def test_wsl_failure_raises(self):
        with patch("geoff.clipboard._is_wsl", return_value=True):
            with patch("geoff.clipboard._get_clip_exe_path", return_value=None):
                with patch("geoff.clipboard.logger"):
                    with pytest.raises(ClipboardError):
                        copy_to_clipboard("test")

    def test_non_wsl_uses_pyperclip(self):
        mock_pyperclip = MagicMock()

        def mock_import(name, *args, **kwargs):
            if name == "pyperclip":
                return mock_pyperclip
            return __import__(name, *args, **kwargs)

        with patch("geoff.clipboard._is_wsl", return_value=False):
            with patch("builtins.__import__", mock_import):
                copy_to_clipboard("test prompt")

        mock_pyperclip.copy.assert_called_once_with("test prompt")

    def test_non_wsl_failure_raises(self):
        def mock_import(name, *args, **kwargs):
            if name == "pyperclip":
                mock = MagicMock()
                mock.copy.side_effect = Exception("error")
                return mock
            return __import__(name, *args, **kwargs)

        with patch("geoff.clipboard._is_wsl", return_value=False):
            with patch("builtins.__import__", mock_import):
                with patch("geoff.clipboard.logger"):
                    with pytest.raises(ClipboardError):
                        copy_to_clipboard("test")

    def test_empty_string(self):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")

        with patch("geoff.clipboard._is_wsl", return_value=True):
            with patch("subprocess.Popen", return_value=mock_process):
                with patch(
                    "geoff.clipboard._get_clip_exe_path",
                    return_value="/mnt/c/Windows/System32/clip.exe",
                ):
                    copy_to_clipboard("")

        mock_process.communicate.assert_called_once_with(b"")

    def test_multiline_string(self):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")
        multiline = "line1\nline2"

        with patch("geoff.clipboard._is_wsl", return_value=True):
            with patch("subprocess.Popen", return_value=mock_process):
                with patch(
                    "geoff.clipboard._get_clip_exe_path",
                    return_value="/mnt/c/Windows/System32/clip.exe",
                ):
                    copy_to_clipboard(multiline)

        mock_process.communicate.assert_called_once_with(b"line1\nline2")
