from pathlib import Path
from dataclasses import asdict
from typing import Any, Dict

from geoff.config import PromptConfig
from geoff.config_io import load_yaml, save_yaml


class ConfigManager:
    def __init__(self, working_dir: Path | None = None):
        self.working_dir = working_dir or Path.cwd()
        self.global_config_path = Path.home() / ".geoff" / "geoff.yaml"
        self.repo_config_path = self.working_dir / ".geoff" / "geoff.yaml"

    @staticmethod
    def get_builtin_defaults() -> PromptConfig:
        return PromptConfig()

    def load_global_config(self) -> Dict[str, Any]:
        return load_yaml(self.global_config_path) or {}

    def load_repo_config(self) -> Dict[str, Any]:
        return load_yaml(self.repo_config_path) or {}

    def resolve_config(self) -> PromptConfig:
        defaults = asdict(self.get_builtin_defaults())
        global_conf = self.load_global_config()
        repo_conf = self.load_repo_config()

        # Merge: defaults -> global -> repo
        merged = defaults.copy()
        merged.update(global_conf)
        merged.update(repo_conf)

        # Filter keys to ensure they match PromptConfig fields
        valid_keys = defaults.keys()
        filtered = {k: v for k, v in merged.items() if k in valid_keys}

        return PromptConfig(**filtered)

    def save_repo_config(self, config: PromptConfig) -> None:
        data = asdict(config)
        save_yaml(self.repo_config_path, data)
