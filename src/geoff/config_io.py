from pathlib import Path
from typing import Dict, Any, Optional
import yaml


def load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    """Safely load YAML file. Return None if file does not exist."""
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        # We might want to log this in a real app, but for now safe fail
        return None


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    """Write dictionary to YAML file."""
    # Ensure directory exists
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False)


def ensure_config_dir(path: Path) -> None:
    """Ensure the configuration directory exists."""
    path.mkdir(parents=True, exist_ok=True)
