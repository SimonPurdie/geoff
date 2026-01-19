import importlib
import pytest


def test_dependencies_installed():
    """Verify that core dependencies are installed and importable."""
    dependencies = [
        "textual",
        "yaml",  # pyyaml imports as yaml
        "pyperclip",
    ]

    for dep in dependencies:
        try:
            importlib.import_module(dep)
        except ImportError:
            pytest.fail(f"Could not import {dep}")


def test_geoff_package_importable():
    """Verify that the geoff package is importable."""
    try:
        import geoff
    except ImportError:
        pytest.fail("Could not import geoff package")
