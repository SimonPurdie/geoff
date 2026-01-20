from pathlib import Path
from dataclasses import asdict, fields
from typing import Any, Dict, Set

from geoff.config import PromptConfig
from geoff.config_io import load_yaml, save_yaml


BASE_PROMPT_STRING_KEYS: Set[str] = {
    "prompt_backpressure_header",
    "prompt_backpressure_lines",
    "prompt_breadcrumb_instruction",
    "prompt_tasklist_study",
    "prompt_tasklist_update",
}


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

    def _resolve_base_prompt_strings(
        self,
        user_conf: Dict[str, Any],
        repo_conf: Dict[str, Any],
        defaults_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        result = {}
        for key in BASE_PROMPT_STRING_KEYS:
            if key in user_conf:
                result[key] = user_conf[key]
            elif key in repo_conf:
                result[key] = repo_conf[key]
            else:
                result[key] = defaults_dict[key]
        return result

    def _materialize_base_prompt_strings(
        self, user_conf: Dict[str, Any], repo_conf: Dict[str, Any]
    ) -> None:
        defaults_dict = asdict(self.get_builtin_defaults())

        resolved_base = self._resolve_base_prompt_strings(
            user_conf, repo_conf, defaults_dict
        )

        to_materialize: Dict[str, Any] = {}
        for key in BASE_PROMPT_STRING_KEYS:
            if key not in user_conf:
                to_materialize[key] = resolved_base[key]

        if not to_materialize:
            return

        if not user_conf:
            merged = to_materialize
            save_yaml(self.global_config_path, merged)
            return

        merged = user_conf.copy()
        merged.update(to_materialize)
        save_yaml(self.global_config_path, merged)

    def resolve_config(self) -> PromptConfig:
        defaults = asdict(self.get_builtin_defaults())
        global_conf = self.load_global_config()
        repo_conf = self.load_repo_config()

        non_base_keys = {
            k: v for k, v in defaults.items() if k not in BASE_PROMPT_STRING_KEYS
        }

        merged_non_base = non_base_keys.copy()
        merged_non_base.update(global_conf)
        merged_non_base.update(repo_conf)

        resolved_base = self._resolve_base_prompt_strings(
            global_conf, repo_conf, defaults
        )

        final_config = {**merged_non_base, **resolved_base}

        valid_keys = defaults.keys()
        filtered = {k: v for k, v in final_config.items() if k in valid_keys}

        resolved = PromptConfig(**filtered)

        self._materialize_base_prompt_strings(global_conf, repo_conf)

        return resolved

    def save_repo_config(self, config: PromptConfig) -> None:
        data = asdict(config)
        for key in BASE_PROMPT_STRING_KEYS:
            data.pop(key, None)
        save_yaml(self.repo_config_path, data)
