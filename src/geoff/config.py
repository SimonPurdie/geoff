from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class PromptConfig:
    study_docs: List[str] = field(default_factory=lambda: ["docs/SPEC.md"])
    breadcrumbs_file: str = "docs/BREADCRUMBS.md"
    task_mode: Literal["tasklist", "oneoff"] = "tasklist"
    tasklist_file: str = "docs/PLAN.md"
    oneoff_prompt: str = ""
    backpressure_enabled: bool = True
    breadcrumb_enabled: bool = True
    theme: str = "catppuccin-mocha"
    max_iterations: int = 0
    max_stuck: int = 2
    prompt_tasklist_study: str = "follow {tasklist} and choose the most important item to address. Complete that item and no other."
    prompt_tasklist_update: str = "Update {tasklist} when the task is done. If you discover issues, immediately update {tasklist} with your findings. When resolved, update {tasklist} and remove the item."
    prompt_backpressure_header: str = "IMPORTANT:"
    prompt_backpressure_lines: List[str] = field(
        default_factory=lambda: [
            "- After implementing functionality or resolving problems, run the tests for that unit of code that was improved.",
            "- If functionality is missing then it's your job to add it as per the application specifications.",
            "- after performing your task run the tests",
            "- when tests pass, commit to deploy changes",
        ]
    )
    prompt_breadcrumb_instruction: str = (
        "if you ran into difficulties due to a lack of information about the project or environment, "
        "which you then resolved, leave a note about it in {breadcrumbs} to help future agents. "
        "For example, if you run commands multiple times before learning the correct command. "
        "IMPORTANT: keep {breadcrumbs} operational only - status updates and progress notes do not belong there."
    )
