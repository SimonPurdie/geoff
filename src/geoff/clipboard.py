import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def _is_wsl():
    """Check if running in Windows Subsystem for Linux."""
    if "WSL_DISTRO_NAME" in os.environ or "WSLENV" in os.environ:
        return True
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def _get_clip_exe_path():
    """Get path to Windows clip.exe in WSL."""
    for path in [
        "/mnt/c/Windows/System32/clip.exe",
        "/mnt/c/Windows/SysWOW64/clip.exe",
    ]:
        if os.path.exists(path):
            return path
    return None


def _copy_with_clip_exe(text: str) -> None:
    """Copy using Windows clip.exe from WSL."""
    clip_path = _get_clip_exe_path()
    if not clip_path:
        raise RuntimeError("clip.exe not found")
    process = subprocess.Popen(
        [clip_path], stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(text.encode("utf-8"))
    if process.returncode != 0:
        raise RuntimeError(f"clip.exe failed: {stderr.decode()}")


class ClipboardError(Exception):
    """Raised when clipboard operations fail."""

    pass


def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard. Raises ClipboardError on failure."""
    if _is_wsl():
        try:
            _copy_with_clip_exe(text)
            return
        except Exception as e:
            logger.error(f"WSL clipboard failed: {e}")
            raise ClipboardError(f"Failed to copy: {e}") from e
    else:
        try:
            import pyperclip

            pyperclip.copy(text)
        except Exception as e:
            logger.error(f"Clipboard failed: {e}")
            raise ClipboardError(f"Failed to copy: {e}") from e
