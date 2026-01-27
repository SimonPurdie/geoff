from pathlib import Path
from typing import List

from geoff.config import PromptConfig


class PromptValidator:
    def __init__(self, execution_dir: Path | None = None):
        self.execution_dir = execution_dir or Path.cwd()

    def validate(self, config: PromptConfig) -> List[str]:
        errors: List[str] = []

        for doc in config.study_docs:
            if not doc or not doc.strip():
                errors.append("Study doc path cannot be empty")
            else:
                doc_path = self.execution_dir / doc
                if not doc_path.exists():
                    errors.append(f"Study doc file not found: {doc}")

        if config.breadcrumb_enabled:
            if not config.breadcrumbs_file or not config.breadcrumbs_file.strip():
                errors.append(
                    "Breadcrumbs file path cannot be empty when breadcrumb is enabled"
                )
            else:
                breadcrumbs_path = self.execution_dir / config.breadcrumbs_file
                try:
                    if not breadcrumbs_path.exists():
                        # Check if filename is valid before creating
                        try:
                            # Validate the filename by attempting to create the path
                            breadcrumbs_path.parent.mkdir(parents=True, exist_ok=True)
                            breadcrumbs_path.write_text("")
                        except (OSError, ValueError, PermissionError) as e:
                            errors.append(
                                f"Invalid breadcrumbs file path: {config.breadcrumbs_file}"
                            )
                except (OSError, PermissionError):
                    # Can't even check if file exists due to permissions
                    errors.append(
                        f"Invalid breadcrumbs file path: {config.breadcrumbs_file}"
                    )

        if config.task_mode == "tasklist":
            if not config.tasklist_file or not config.tasklist_file.strip():
                errors.append("Tasklist file path cannot be empty in tasklist mode")
            else:
                tasklist_path = self.execution_dir / config.tasklist_file
                if not tasklist_path.exists():
                    errors.append(f"Tasklist file not found: {config.tasklist_file}")
        elif config.task_mode == "oneoff":
            if not config.oneoff_prompt or not config.oneoff_prompt.strip():
                errors.append("One-off prompt cannot be empty in one-off mode")

        if config.max_iterations < 0:
            errors.append("Max iterations must be >= 0")

        if config.max_stuck < 0:
            errors.append("Max stuck must be >= 0")

        if config.max_frozen < 0:
            errors.append("Frozen must be >= 0")

        return errors

    def is_valid(self, config: PromptConfig) -> bool:
        return len(self.validate(config)) == 0
